from src.operank_scheduling.algo.distribution_models import (
    distribute_timeslots_to_days,
    distribute_timeslots_to_operating_rooms,
)
from src.operank_scheduling.models.operank_models import OperatingRoom, Timeslot


def test_preliminary_scheduling_flow():
    timeslot_list = [Timeslot(duration=60 * ((i % 3) + 1)) for i in range(10)]
    or_list = [OperatingRoom(id=f"o{i}", properties=[], uuid=i) for i in range(2)]
    distribute_timeslots_to_operating_rooms(timeslot_list, or_list)
    distribute_timeslots_to_days(or_list)
