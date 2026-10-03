from core.assessment_persistence import AssessmentPersistence
from core.assessment_query import AssessmentQuery
from core.assessment_snapshot import AssessmentSnapshot


def make_snapshot(
    assessment_id,
    target,
    started_at,
    finding_count=1,
):
    return AssessmentSnapshot(
        assessment_id=assessment_id,
        target=target,
        started_at=started_at,
        finding_count=finding_count,
        severity_counts={"info": finding_count},
        sources=["host_intelligence"],
    )


def test_query_lists_persisted_snapshots(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-002",
            "localhost",
            "2026-09-29T13:00:00+00:00",
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-001",
            "localhost",
            "2026-09-29T12:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    result = query.list_snapshots()

    assert [snapshot.assessment_id for snapshot in result] == [
        "assessment-001",
        "assessment-002",
    ]


def test_query_gets_snapshot_by_id(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    result = query.get_snapshot("assessment-001")

    assert result.assessment_id == "assessment-001"
    assert result.target == "host-a"


def test_query_lists_targets_deterministically(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-002",
            "z-host",
            "2026-09-29T12:00:00+00:00",
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-001",
            "a-host",
            "2026-09-29T13:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    assert query.list_targets() == [
        "a-host",
        "z-host",
    ]


def test_query_groups_snapshots_by_target_chronologically(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    for snapshot in (
        make_snapshot(
            "assessment-003",
            "host-a",
            "2026-09-29T14:00:00+00:00",
        ),
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        ),
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
        ),
    ):
        persistence.save(snapshot)

    query = AssessmentQuery(persistence)

    result = query.list_snapshots_by_target()

    assert [
        snapshot.assessment_id
        for snapshot in result["host-a"]
    ] == [
        "assessment-001",
        "assessment-002",
        "assessment-003",
    ]


def test_query_gets_latest_snapshot_for_each_target(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-003",
            "host-b",
            "2026-09-29T14:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    result = query.get_latest_snapshots_by_target()

    assert result["host-a"].assessment_id == "assessment-002"
    assert result["host-b"].assessment_id == "assessment-003"


def test_query_gets_latest_snapshot_pair_for_target(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    for snapshot in (
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        ),
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
        ),
        make_snapshot(
            "assessment-003",
            "host-a",
            "2026-09-29T14:00:00+00:00",
        ),
    ):
        persistence.save(snapshot)

    query = AssessmentQuery(persistence)

    previous, latest = query.get_latest_snapshot_pair_for_target(
        "host-a"
    )

    assert previous.assessment_id == "assessment-002"
    assert latest.assessment_id == "assessment-003"


def test_query_returns_none_for_target_without_two_snapshots(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    assert query.get_latest_snapshot_pair_for_target("host-a") is None


def test_query_gets_latest_snapshot_globally(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-b",
            "2026-09-29T14:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    latest = query.get_latest_snapshot()

    assert latest is not None
    assert latest.assessment_id == "assessment-002"


def test_query_lists_consecutive_snapshot_pairs_for_target(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    for snapshot in (
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        ),
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
        ),
        make_snapshot(
            "assessment-003",
            "host-a",
            "2026-09-29T14:00:00+00:00",
        ),
    ):
        persistence.save(snapshot)

    query = AssessmentQuery(persistence)

    pairs = query.list_snapshot_pairs_for_target("host-a")

    assert [
        (previous.assessment_id, current.assessment_id)
        for previous, current in pairs
    ] == [
        ("assessment-001", "assessment-002"),
        ("assessment-002", "assessment-003"),
    ]


def test_query_returns_empty_snapshot_history_for_unknown_target(
    tmp_path,
):
    persistence = AssessmentPersistence(tmp_path)
    query = AssessmentQuery(persistence)

    assert query.list_snapshots_for_target("unknown") == []


def test_query_returns_none_when_no_snapshots_exist(tmp_path):
    persistence = AssessmentPersistence(tmp_path)
    query = AssessmentQuery(persistence)

    assert query.get_latest_snapshot() is None


def test_query_gets_latest_snapshot_for_target(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    latest = query.get_latest_snapshot_for_target("host-a")

    assert latest is not None
    assert latest.assessment_id == "assessment-002"


def test_query_lists_assessment_ids(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-002",
            "host-a",
            "2026-09-29T13:00:00+00:00",
        )
    )
    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    assert query.list_assessment_ids() == [
        "assessment-001",
        "assessment-002",
    ]


def test_query_gets_snapshot_by_id(tmp_path):
    persistence = AssessmentPersistence(tmp_path)

    persistence.save(
        make_snapshot(
            "assessment-001",
            "host-a",
            "2026-09-29T12:00:00+00:00",
        )
    )

    query = AssessmentQuery(persistence)

    result = query.get_snapshot("assessment-001")

    assert result.assessment_id == "assessment-001"
    assert result.target == "host-a"
