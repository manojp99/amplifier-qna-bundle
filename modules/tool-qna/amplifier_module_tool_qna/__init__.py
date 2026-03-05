"""Amplifier Q&A Tool – structured requirements gathering through guided questionnaires."""

from __future__ import annotations

import json
import uuid
from typing import Any

from amplifier_core import ModuleCoordinator

from .models import Answer, Note, Question, QuestionType, Session, Template
from .reports import generate_json_report, generate_markdown_report
from .templates import TEMPLATES

__all__ = ["mount", "QnATool"]

_DEFAULT_QUESTIONS_PER_BATCH = 5


async def mount(coordinator: ModuleCoordinator, config: dict) -> QnATool:
    """Amplifier module entry point. Mounts the Q&A tool against the coordinator.

    Supported config keys:

    - ``custom_templates_dir`` (str): Path to a directory containing custom
      YAML template files.  Templates found here are merged with the built-in
      set; custom templates with the same ID as a built-in will **override**
      the built-in.
    - ``questions_per_batch`` (int): Number of questions returned per batch
      by ``get_questions`` and ``start_session``.  Defaults to 5.
    """
    tool = QnATool(
        custom_templates_dir=config.get("custom_templates_dir"),
        questions_per_batch=int(
            config.get("questions_per_batch", _DEFAULT_QUESTIONS_PER_BATCH)
        ),
    )
    await coordinator.mount("tools", tool, name="qna")
    return tool


def _format_question(q: Question) -> str:
    """Format a single question for display."""
    parts: list[str] = []
    type_label = q.type.value.replace("_", " ")
    required_marker = " *(required)*" if q.required else ""
    parts.append(f"- **[{q.id}]** ({type_label}{required_marker}) {q.text}")

    if q.options:
        opts = " | ".join(q.options)
        parts.append(f"  Options: {opts}")
    if q.type == QuestionType.SCALE:
        parts.append(f"  Scale: {q.scale_min}–{q.scale_max}")
    if q.hint:
        parts.append(f"  *Hint: {q.hint}*")

    return "\n".join(parts)


class QnATool:
    """Amplifier tool for structured Q&A requirements gathering.

    Implements the Amplifier Tool protocol: name, description, input_schema
    properties and an async execute() method.
    """

    def __init__(
        self,
        custom_templates_dir: str | None = None,
        questions_per_batch: int = _DEFAULT_QUESTIONS_PER_BATCH,
    ) -> None:
        self._sessions: dict[str, Session] = {}
        self._questions_per_batch = questions_per_batch

        # Start with built-in templates, then merge custom ones on top
        self._templates: dict[str, Template] = dict(TEMPLATES)
        if custom_templates_dir:
            from .loader import load_templates_from_directory

            custom = load_templates_from_directory(custom_templates_dir)
            self._templates.update(custom)

    @property
    def name(self) -> str:
        return "qna"

    @property
    def description(self) -> str:
        return (
            "Structured Q&A tool for gathering requirements. "
            "Start a guided questionnaire session using a built-in template "
            "(software requirements, user stories, bug reports, or project kickoff), "
            "then record answers interactively and generate a formatted report."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "required": ["operation"],
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "list_templates",
                        "start_session",
                        "get_questions",
                        "record_answer",
                        "record_note",
                        "get_progress",
                        "generate_report",
                    ],
                    "description": "The operation to perform",
                },
                "topic": {
                    "type": "string",
                    "description": "Topic/subject for the Q&A session (for start_session)",
                },
                "template": {
                    "type": "string",
                    "description": "Template ID to use (for start_session). Use list_templates to see options.",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID (for get_questions, record_answer, get_progress, generate_report)",
                },
                "question_id": {
                    "type": "string",
                    "description": "Question ID being answered (for record_answer)",
                },
                "answer": {
                    "type": ["string", "array", "number", "boolean"],
                    "description": "The user's answer (for record_answer)",
                },
                "note": {
                    "type": "string",
                    "description": "Freeform observation or follow-up detail (for record_note)",
                },
                "section_id": {
                    "type": "string",
                    "description": "Optionally attach the note to a template section (for record_note)",
                },
                "format": {
                    "type": "string",
                    "enum": ["markdown", "json"],
                    "default": "markdown",
                    "description": "Output format (for generate_report)",
                },
            },
        }

    async def execute(self, input: dict[str, Any]) -> str:
        """Route to the requested operation and return a text result."""
        op = input.get("operation")
        try:
            if op == "list_templates":
                return self._list_templates()
            if op == "start_session":
                return self._start_session(input)
            if op == "get_questions":
                return self._get_questions(input)
            if op == "record_answer":
                return self._record_answer(input)
            if op == "record_note":
                return self._record_note(input)
            if op == "get_progress":
                return self._get_progress(input)
            if op == "generate_report":
                return self._generate_report(input)
            return f"Unknown operation: {op}"
        except (KeyError, ValueError, TypeError) as exc:
            return f"Error: {exc}"

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def _list_templates(self) -> str:
        lines: list[str] = ["**Available Q&A Templates**\n"]
        for t in self._templates.values():
            q_count = sum(len(s.questions) for s in t.sections)
            section_names = ", ".join(s.title for s in t.sections)
            lines.append(f"- **{t.id}** – {t.name}")
            lines.append(f"  {t.description}")
            lines.append(f"  Sections: {section_names} | Questions: {q_count}")
            lines.append("")
        lines.append("Use `start_session` with a template ID and topic to begin.")
        return "\n".join(lines)

    def _start_session(self, input: dict[str, Any]) -> str:
        template_id = input.get("template", "")
        topic = input.get("topic", "")

        if not template_id:
            return "Error: 'template' is required for start_session."
        if not topic:
            return "Error: 'topic' is required for start_session."
        if template_id not in self._templates:
            available = ", ".join(self._templates)
            return f"Error: Unknown template '{template_id}'. Available: {available}"

        session_id = uuid.uuid4().hex[:8]
        template = self._templates[template_id]
        session = Session(id=session_id, topic=topic, template=template)
        self._sessions[session_id] = session

        # Return the first batch of questions
        first_batch = session.active_questions[: self._questions_per_batch]
        q_lines = "\n".join(_format_question(q) for q in first_batch)

        total = session.total_applicable_questions
        return (
            f"Session started: **{session_id}**\n"
            f"Template: {template.name}\n"
            f"Topic: {topic}\n"
            f"Total questions: {total}\n\n"
            f"**First questions:**\n\n{q_lines}\n\n"
            f"Use `record_answer` with the session_id, question_id, and your answer."
        )

    def _get_questions(self, input: dict[str, Any]) -> str:
        session = self._resolve_session(input)
        pending = session.active_questions

        if not pending:
            return (
                f"Session **{session.id}** is complete! "
                f"All applicable questions have been answered. "
                f"Use `generate_report` to produce the final document."
            )

        batch = pending[: self._questions_per_batch]
        remaining = len(pending) - len(batch)
        q_lines = "\n".join(_format_question(q) for q in batch)

        result = f"**Questions for session {session.id}** (progress: {session.progress_pct}%)\n\n{q_lines}"
        if remaining > 0:
            result += f"\n\n*{remaining} more question(s) after these.*"
        return result

    def _record_answer(self, input: dict[str, Any]) -> str:
        session = self._resolve_session(input)

        question_id = input.get("question_id")
        if not question_id:
            return "Error: 'question_id' is required for record_answer."
        if "answer" not in input:
            return "Error: 'answer' is required for record_answer."

        raw_answer = input["answer"]

        # Find the question definition
        question: Question | None = None
        for section in session.template.sections:
            for q in section.questions:
                if q.id == question_id:
                    question = q
                    break
            if question:
                break

        if question is None:
            return f"Error: Unknown question_id '{question_id}' in this template."

        # Validate the answer against question type
        validated = self._validate_answer(question, raw_answer)

        session.answers[question_id] = Answer(
            question_id=question_id,
            value=validated,
            question_text=question.text,
        )

        # Check if new questions were unlocked by this answer
        active = session.active_questions
        response = (
            f"Recorded answer for **{question_id}**.\n"
            f"Progress: {session.progress_pct}% ({len(session.answers)}/{session.total_applicable_questions})"
        )

        if not active:
            response += (
                "\n\nAll questions answered! "
                "Use `generate_report` to produce the final document."
            )
        else:
            next_q = active[0]
            response += f"\n\nNext question: **[{next_q.id}]** {next_q.text}"

        return response

    def _record_note(self, input: dict[str, Any]) -> str:
        session = self._resolve_session(input)

        text = input.get("note")
        if not text:
            return "Error: 'note' is required for record_note."

        section_id = input.get("section_id")
        if section_id:
            valid_ids = [s.id for s in session.template.sections]
            if section_id not in valid_ids:
                return (
                    f"Error: Unknown section_id '{section_id}'. "
                    f"Valid sections: {', '.join(valid_ids)}"
                )

        session.notes.append(Note(text=str(text), section_id=section_id))

        label = f" (section: {section_id})" if section_id else ""
        return f"Note recorded{label}.\nTotal notes in session: {len(session.notes)}"

    def _get_progress(self, input: dict[str, Any]) -> str:
        session = self._resolve_session(input)

        lines: list[str] = [
            f"**Session {session.id}** – {session.topic}",
            f"Overall progress: {session.progress_pct}% ({len(session.answers)}/{session.total_applicable_questions})",
            "",
        ]

        for section in session.template.sections:
            total_in_section = 0
            answered_in_section = 0
            for q in section.questions:
                is_applicable = q.condition is None
                if q.condition:
                    dep_id, expected = q.condition
                    if (
                        dep_id in session.answers
                        and session.answers[dep_id].value == expected
                    ):
                        is_applicable = True
                if is_applicable:
                    total_in_section += 1
                    if q.id in session.answers:
                        answered_in_section += 1

            if total_in_section == 0:
                status = "n/a"
            elif answered_in_section == total_in_section:
                status = "complete"
            elif answered_in_section > 0:
                status = "in progress"
            else:
                status = "not started"

            lines.append(
                f"- **{section.title}**: {answered_in_section}/{total_in_section} ({status})"
            )

        if session.is_complete:
            lines.append("\nAll questions answered. Ready to generate report.")

        return "\n".join(lines)

    def _generate_report(self, input: dict[str, Any]) -> str:
        session = self._resolve_session(input)
        fmt = input.get("format", "markdown")

        if not session.answers:
            return "Error: No answers recorded yet. Answer some questions first."

        if fmt == "json":
            report_data = generate_json_report(session)
            return json.dumps(report_data, indent=2)

        return generate_markdown_report(session)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_session(self, input: dict[str, Any]) -> Session:
        session_id = input.get("session_id")
        if not session_id:
            raise ValueError("'session_id' is required for this operation.")
        if session_id not in self._sessions:
            raise ValueError(
                f"Unknown session_id '{session_id}'. Start a session first."
            )
        return self._sessions[session_id]

    @staticmethod
    def _validate_answer(question: Question, raw: Any) -> Any:
        """Coerce and validate the raw answer against the question type."""
        qtype = question.type

        if qtype == QuestionType.YES_NO:
            if isinstance(raw, bool):
                return raw
            if isinstance(raw, str):
                lowered = raw.strip().lower()
                if lowered in ("yes", "y", "true", "1"):
                    return True
                if lowered in ("no", "n", "false", "0"):
                    return False
            raise ValueError(
                f"Question '{question.id}' expects a yes/no answer. Got: {raw!r}"
            )

        if qtype == QuestionType.CHOICE:
            val = str(raw)
            if question.options and val not in question.options:
                raise ValueError(
                    f"Question '{question.id}' expects one of {question.options}. Got: {val!r}"
                )
            return val

        if qtype == QuestionType.MULTI_CHOICE:
            if isinstance(raw, str):
                items = [s.strip() for s in raw.split(",")]
            elif isinstance(raw, list):
                items = [str(v) for v in raw]
            else:
                items = [str(raw)]
            if question.options:
                invalid = [i for i in items if i not in question.options]
                if invalid:
                    raise ValueError(
                        f"Question '{question.id}': invalid choice(s) {invalid}. "
                        f"Valid options: {question.options}"
                    )
            return items

        if qtype == QuestionType.SCALE:
            try:
                val = int(raw)
            except (TypeError, ValueError):
                raise ValueError(
                    f"Question '{question.id}' expects an integer "
                    f"({question.scale_min}–{question.scale_max}). Got: {raw!r}"
                ) from None
            if not (question.scale_min <= val <= question.scale_max):
                raise ValueError(
                    f"Question '{question.id}' expects a value between "
                    f"{question.scale_min} and {question.scale_max}. Got: {val}"
                )
            return val

        # TEXT – accept anything as string
        return str(raw)
