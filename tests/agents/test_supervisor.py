from agents.supervisor.schedule import BEAT_SCHEDULE


def test_schedule_has_required_tasks():
    assert "discover-trending" in BEAT_SCHEDULE
    assert "harvest-threads" in BEAT_SCHEDULE
    assert "cleanup-watchlist" in BEAT_SCHEDULE


def test_schedule_intervals():
    assert BEAT_SCHEDULE["discover-trending"]["schedule"].run_every.total_seconds() == 90
    assert BEAT_SCHEDULE["harvest-threads"]["schedule"].run_every.total_seconds() == 20
    assert BEAT_SCHEDULE["cleanup-watchlist"]["schedule"].run_every.total_seconds() == 300
