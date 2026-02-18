"""Data models for the Q&A tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QuestionType(Enum):
    TEXT = "text"
    CHOICE = "choice"
    MULTI_CHOICE = "multi_choice"
    YES_NO = "yes_no"
    SCALE = "scale"


@dataclass
class Question:
    id: str
    text: str
    type: QuestionType
    required: bool = True
    options: list[str] | None = None
    scale_min: int = 1
    scale_max: int = 5
    condition: tuple[str, Any] | None = None
    hint: str | None = None


@dataclass
class Section:
    id: str
    title: str
    description: str
    questions: list[Question]
    guidance: str | None = None  # LLM direction: what to explore, tone, depth


@dataclass
class Note:
    """A freeform observation captured by the LLM during the Q&A session.

    Notes are not tied to a specific template question.  They capture insights,
    follow-up details, or requirements that emerged organically during the
    conversation but don't fit any predefined question.
    """

    text: str
    section_id: str | None = None  # optional: attach to a template section


@dataclass
class Template:
    id: str
    name: str
    description: str
    sections: list[Section]


@dataclass
class Answer:
    question_id: str
    value: Any
    question_text: str


@dataclass
class Session:
    id: str
    topic: str
    template: Template
    answers: dict[str, Answer] = field(default_factory=dict)
    notes: list[Note] = field(default_factory=list)

    @property
    def active_questions(self) -> list[Question]:
        """Return questions that should be shown (conditions met, not yet answered)."""
        result: list[Question] = []
        for section in self.template.sections:
            for q in section.questions:
                if q.id in self.answers:
                    continue
                if q.condition:
                    dep_id, expected = q.condition
                    if dep_id not in self.answers:
                        continue
                    if self.answers[dep_id].value != expected:
                        continue
                result.append(q)
        return result

    @property
    def total_applicable_questions(self) -> int:
        """Count questions whose conditions are met or have no conditions."""
        count = 0
        for section in self.template.sections:
            for q in section.questions:
                if q.condition is None:
                    count += 1
                else:
                    dep_id, expected = q.condition
                    if (
                        dep_id in self.answers
                        and self.answers[dep_id].value == expected
                    ):
                        count += 1
        return count

    @property
    def progress_pct(self) -> int:
        total = self.total_applicable_questions
        if total == 0:
            return 100
        return int(len(self.answers) / total * 100)

    @property
    def is_complete(self) -> bool:
        return len(self.active_questions) == 0
