"""Parse structured LLM assessment output (scores + narrative sections) for mentor draft fill-in."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

_SCORE_LINE = re.compile(
    r"^\s*(Quality|Readability|Correctness)\s*[:：]\s*([1-5])\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedAiAssessment:
    """Scores and narrative extracted from model output; full text is stored separately on AiDraft."""

    quality_score: Optional[int]
    readability_score: Optional[int]
    correctness_score: Optional[int]
    narrative_feedback: Optional[str]
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _split_markdown_sections(text: str) -> dict[str, str]:
    """Split body by ## / ### headings; keys are normalized lowercase heading text."""
    lines = text.splitlines()
    sections: dict[str, list[str]] = {}
    current_key: Optional[str] = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip().lower()
            current_key = title
            sections.setdefault(current_key, [])
            continue
        if current_key is not None:
            sections[current_key].append(line)
    out: dict[str, str] = {}
    for k, vlines in sections.items():
        body = "\n".join(vlines).strip()
        if body:
            out[k] = body
    return out


def _extract_feedback_suggestions(text: str) -> tuple[Optional[str], Optional[str], tuple[str, ...]]:
    warnings: list[str] = []
    sections = _split_markdown_sections(text)

    def _body_for(*needles: str) -> Optional[str]:
        for needle in needles:
            for k, body in sections.items():
                if k == needle or k.startswith(needle + " ") or needle in k:
                    return body
        return None

    fb = _body_for("feedback on the code", "feedback")
    sug = _body_for("suggestions to improve", "suggestions")

    if fb is None and sug is None:
        m_fb = re.search(
            r"(?is)feedback\s+on\s+the\s+code\s*[:：]?\s*(.*?)(?=suggestions\s+to\s+improve|$)",
            text,
        )
        m_sug = re.search(r"(?is)suggestions\s+to\s+improve\s*[:：]?\s*(.*)\Z", text)
        if m_fb:
            fb = (m_fb.group(1) or "").strip() or None
        if m_sug:
            sug = (m_sug.group(1) or "").strip() or None

    if fb is None and sug is None:
        warnings.append("missing_feedback_sections")

    return fb, sug, tuple(warnings)


def parse_ai_assessment_output(text: str) -> ParsedAiAssessment:
    """
    Expect lines near the top: Quality: N, Readability: N, Correctness: N (each 1–5),
    plus sections 'Feedback on the code' and 'Suggestions to improve' (markdown ### headings preferred).
    """
    warnings: list[str] = []
    q: Optional[int] = None
    r: Optional[int] = None
    c: Optional[int] = None

    for line in text.splitlines()[:60]:
        m = _SCORE_LINE.match(line)
        if not m:
            continue
        label, val = m.group(1).lower(), int(m.group(2))
        if label == "quality":
            q = val
        elif label == "readability":
            r = val
        elif label == "correctness":
            c = val

    if q is None or r is None or c is None:
        warnings.append("incomplete_scores")

    fb, sug, sec_warnings = _extract_feedback_suggestions(text)
    warnings.extend(sec_warnings)

    narrative: Optional[str] = None
    parts = [p for p in (fb, sug) if p and p.strip()]
    if parts:
        narrative = "\n\n".join(parts)
    elif text.strip():
        narrative = text.strip()
        warnings.append("fallback_narrative_full_text")

    return ParsedAiAssessment(
        quality_score=q,
        readability_score=r,
        correctness_score=c,
        narrative_feedback=narrative,
        warnings=tuple(dict.fromkeys(warnings)),
    )
