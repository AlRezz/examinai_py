"""Unit tests for structured AI assessment parsing."""

from __future__ import annotations

from examai.ai_assessment_parsing import parse_ai_assessment_output


def test_parse_full_structure() -> None:
    text = """
Quality: 2
Readability: 4
Correctness: 3

### Feedback on the code
First note.

### Suggestions to improve
Second note.
""".strip()
    p = parse_ai_assessment_output(text)
    assert p.quality_score == 2
    assert p.readability_score == 4
    assert p.correctness_score == 3
    assert p.narrative_feedback
    assert "First note" in p.narrative_feedback
    assert "Second note" in p.narrative_feedback
    assert "incomplete_scores" not in p.warnings


def test_parse_fallback_narrative_when_no_headings() -> None:
    text = "Quality: 5\nReadability: 5\nCorrectness: 5\n\nPlain prose only."
    p = parse_ai_assessment_output(text)
    assert p.quality_score == 5
    assert p.readability_score == 5
    assert p.correctness_score == 5
    assert p.narrative_feedback and "Plain prose" in p.narrative_feedback
    assert "fallback_narrative_full_text" in p.warnings
