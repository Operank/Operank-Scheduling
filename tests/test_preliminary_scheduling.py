import datetime

import pytest

from operank_scheduling.algo.surgery_distribution_models import (
    distribute_timeslots_to_days,
    distribute_timeslots_to_operating_rooms,
)
from operank_scheduling.models.operank_models import OperatingRoom, Timeslot
from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
)
from operank_scheduling.models.io_utilities import find_project_root


@pytest.fixture
def scheduling_fixture():
    timeslot_list = [Timeslot(duration=60 * ((i % 3) + 1)) for i in range(10)]
    or_list = [OperatingRoom(id=f"o{i}", properties=[]) for i in range(2)]
    distribute_timeslots_to_operating_rooms(timeslot_list, or_list)
    distribute_timeslots_to_days(or_list)
    return timeslot_list, or_list


def test_no_empty_days(scheduling_fixture):
    timeslot_list, or_list = scheduling_fixture
    for operating_room in or_list:
        for day in operating_room.timeslots_by_day:
            assert len(day) > 0


def test_schedule_to_days(scheduling_fixture):
    timeslot_list, or_list = scheduling_fixture
    for operating_room in or_list:
        operating_room.schedule_timeslots_to_days(datetime.datetime.now().date())


def test_schedule_to_days_with_non_working_days(scheduling_fixture):
    timeslot_list, or_list = scheduling_fixture
    for operating_room in or_list:
        # Try to schedule on friday, expect schedule to start from sunday!
        operating_room.schedule_timeslots_to_days(
            datetime.datetime(year=2023, month=3, day=10).date()
        )
        assert list(operating_room.schedule.keys()) == [
            datetime.datetime(year=2023, month=3, day=12).date(),
            datetime.datetime(year=2023, month=3, day=13).date(),
        ]


def test_scheduling_on_real_operating_rooms():
    root = find_project_root()
    operating_room_data_file = root / "assets" / "example_operating_room_schedule.json"
    operating_rooms = load_operating_rooms_from_json(operating_room_data_file)

    # Retain only first two for now
    or_list = operating_rooms[:2]
    timeslot_list = [Timeslot(duration=60 * ((i % 3) + 1)) for i in range(10)]
    distribute_timeslots_to_operating_rooms(timeslot_list, or_list)
    distribute_timeslots_to_days(or_list)
    for operating_room in or_list:
        operating_room.schedule_timeslots_to_days(datetime.datetime.now().date())
