from __future__ import annotations

import re

CHOICES = ("A", "B", "C", "D")
_CHOICE_PREFIX_RE = re.compile(r"^\s*([ABCD])(?:\s+|[\)\.:\-])\s*", re.IGNORECASE)
_SINGLE_CHOICE_RE = re.compile(r"^\(?\s*([ABCD])\s*\)?\s*[\)\.:\-]?\s*$", re.IGNORECASE)
_INLINE_CHOICE_RE = re.compile(
    r"(?i)\b(?:answer|odpoveď|odpoved|moznost|možnosť)"
    r"\s*[:\-]?\s*\(?\s*([ABCD])\s*\)?\b"
)
_FALLBACK_CHOICE_RE = re.compile(r"\b([ABCD])\b", re.IGNORECASE)


def normalize_ws(text: str) -> str:
    return " ".join((text or "").split())


def normalize_choice(value: str | None) -> str | None:
    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    for pattern in (_SINGLE_CHOICE_RE, _INLINE_CHOICE_RE, _FALLBACK_CHOICE_RE):
        match = pattern.search(text)
        if match:
            return match.group(1).upper()

    return None


def strip_choice_prefix(option: str) -> str:
    normalized = normalize_ws(option)
    match = _CHOICE_PREFIX_RE.match(normalized)
    if match:
        return normalized[match.end():].strip()
    return normalized


def format_option(letter: str, option: str) -> str:
    content = strip_choice_prefix(option)
    return f"{letter}) {content}" if content else f"{letter})"


def format_prompt(question: str, options: list[str]) -> str:
    lines = [normalize_ws(question)]
    for idx, option in enumerate(options):
        letter = CHOICES[idx] if idx < len(CHOICES) else str(idx + 1)
        lines.append(format_option(letter, option))
    return "\n".join(lines)


def choice_to_index(choice: str | None) -> int | None:
    normalized = normalize_choice(choice)
    if normalized is None:
        return None
    return CHOICES.index(normalized)
