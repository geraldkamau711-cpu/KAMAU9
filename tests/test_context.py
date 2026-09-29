from core.context import AssessmentContext


def test_context_creates_id():
    context = AssessmentContext(target="lab-target")

    assert context.target == "lab-target"
    assert context.assessment_id
    assert context.started_at


def test_context_ids_are_unique():
    first = AssessmentContext(target="lab-target")
    second = AssessmentContext(target="lab-target")

    assert first.assessment_id != second.assessment_id
