from agents.supervisor.schedule import BEAT_SCHEDULE


def test_schedule_has_all_tasks():
    expected = [
        "discover-trending", "harvest-threads", "cleanup-watchlist",
        "normalize-items", "update-author-profiles", "analyze-opinions",
        "moderate-items", "map-items-to-metrics", "garden-metrics",
        "compute-rollups", "backfill-stories",
    ]
    for name in expected:
        assert name in BEAT_SCHEDULE, f"Missing task: {name}"


def test_schedule_intervals():
    intervals = {
        "discover-trending": 90,
        "harvest-threads": 20,
        "cleanup-watchlist": 300,
        "normalize-items": 15,
        "update-author-profiles": 60,
        "analyze-opinions": 20,
        "moderate-items": 30,
        "map-items-to-metrics": 20,
        "garden-metrics": 3600,
        "compute-rollups": 45,
        "backfill-stories": 300,
    }
    for name, expected_secs in intervals.items():
        actual = BEAT_SCHEDULE[name]["schedule"].run_every.total_seconds()
        assert actual == expected_secs, f"{name}: {actual} != {expected_secs}"
