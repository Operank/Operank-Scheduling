from src.operank_scheduling.models.operank_models import Timeslot


def test_create_timeslot():
    new_timeslot = Timeslot(0, 60)
    assert repr(new_timeslot) == "Timeslot (60)"
    assert 43 in new_timeslot
    assert 184 not in new_timeslot
