from src.operank_scheduling.models.operank_models import Timeslot, Surgery


def test_timeslot():
    new_timeslot = Timeslot(duration=60)
    assert repr(new_timeslot) == "Timeslot (60)"
    assert 43 in new_timeslot
    assert 184 not in new_timeslot


def test_timeslot_surgery_interaction():
    s = Surgery(name="Colostomy", duration_in_minutes=75)
    t1 = Timeslot(duration=60)
    t2 = Timeslot(duration=120)

    assert s.can_fit_in(t1) is False
    assert s.can_fit_in(t2) is True
