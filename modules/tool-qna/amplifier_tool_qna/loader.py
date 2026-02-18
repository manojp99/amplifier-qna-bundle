"""Load custom Q&A templates from YAML files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .models import Question, QuestionType, Section, Template

logger = logging.getLogger(__name__)


def load_templates_from_directory(directory: str | Path) -> dict[str, Template]:
    """Scan a directory for YAML template files and return parsed templates.

    Each ``.yaml`` / ``.yml`` file in *directory* is expected to contain a
    single template definition.  Files that fail to parse are logged and
    skipped so that one bad file does not break the entire tool.
    """
    import yaml  # imported here so PyYAML is only required when custom templates are used

    path = Path(directory)
    if not path.is_dir():
        logger.warning("Custom templates directory does not exist: %s", path)
        return {}

    templates: dict[str, Template] = {}
    for file in sorted(path.iterdir()):
        if file.suffix not in (".yaml", ".yml"):
            continue
        try:
            raw = yaml.safe_load(file.read_text())
            template = _parse_template(raw, source=str(file))
            templates[template.id] = template
            logger.info("Loaded custom template '%s' from %s", template.id, file.name)
        except Exception:
            logger.exception("Failed to load template from %s", file)

    return templates


def _parse_template(raw: Any, *, source: str = "<unknown>") -> Template:
    """Convert a raw YAML dict into a :class:`Template` instance."""
    if not isinstance(raw, dict):
        msg = f"Template file must contain a YAML mapping, got {type(raw).__name__} ({source})"
        raise TypeError(msg)

    _require_keys(raw, ["id", "name", "description", "sections"], source)

    sections: list[Section] = []
    for raw_section in raw["sections"]:
        sections.append(_parse_section(raw_section, source=source))

    return Template(
        id=raw["id"],
        name=raw["name"],
        description=raw["description"],
        sections=sections,
    )


def _parse_section(raw: dict[str, Any], *, source: str) -> Section:
    _require_keys(raw, ["id", "title", "questions"], source)

    questions: list[Question] = []
    for raw_q in raw["questions"]:
        questions.append(_parse_question(raw_q, source=source))

    return Section(
        id=raw["id"],
        title=raw["title"],
        description=raw.get("description", ""),
        questions=questions,
        guidance=raw.get("guidance"),
    )


def _parse_question(raw: dict[str, Any], *, source: str) -> Question:
    _require_keys(raw, ["id", "text", "type"], source)

    try:
        qtype = QuestionType(raw["type"])
    except ValueError:
        valid = [t.value for t in QuestionType]
        msg = f"Invalid question type '{raw['type']}' in {source}. Valid types: {valid}"
        raise ValueError(msg) from None

    condition: tuple[str, Any] | None = None
    raw_condition = raw.get("condition")
    if raw_condition is not None:
        if isinstance(raw_condition, dict):
            _require_keys(raw_condition, ["question_id", "equals"], source)
            condition = (raw_condition["question_id"], raw_condition["equals"])
        elif isinstance(raw_condition, list) and len(raw_condition) == 2:
            condition = (str(raw_condition[0]), raw_condition[1])

    return Question(
        id=raw["id"],
        text=raw["text"],
        type=qtype,
        required=raw.get("required", True),
        options=raw.get("options"),
        scale_min=raw.get("scale_min", 1),
        scale_max=raw.get("scale_max", 5),
        condition=condition,
        hint=raw.get("hint"),
    )


def _require_keys(d: dict[str, Any], keys: list[str], source: str) -> None:
    missing = [k for k in keys if k not in d]
    if missing:
        msg = f"Missing required keys {missing} in {source}"
        raise KeyError(msg)
