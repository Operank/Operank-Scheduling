from typing import List, Dict
from models.operank_models import OperatingRoom, Surgery
from algo.algo_helpers import intersection_size
from algo.distribution_models import distribute_surgeries_to_operating_rooms, distribute_surgeries_to_days
from loguru import logger

"""
# General Idea
    Take a list of surgeries (w/ their requirements & duration) and a list of rooms (w/ their properties),
    and assign surgeries to rooms, such that:
        1. Surgeries that require special requirements get all of their requirements (1:1 relations only)
        2. If multiple rooms satisfy the requirements, or if no special requirements are given,
           assign surgeries to rooms such that the total duration is close to even.
        3. For each room, assign surgeries to days, such that minimum days are required.
"""


def find_suitable_rooms_for_surgery(
    surgery: Surgery, list_of_rooms: List[OperatingRoom]
) -> List:
    assert surgery.requirements
    suitable_rooms = []
    for room in list_of_rooms:
        match_strength = intersection_size(surgery.requirements, room.properties)
        if match_strength >= len(surgery.requirements):
            suitable_rooms.append(room)
    return suitable_rooms


def find_suitable_rooms_for_special_surgeries(
    list_of_surgeries: List[Surgery], list_of_rooms: List[OperatingRoom]
) -> Dict[Surgery, List[OperatingRoom]]:
    special_surgery_mapping = dict()
    for surgery in list_of_surgeries:
        special_surgery_mapping[surgery] = find_suitable_rooms_for_surgery(
            surgery, list_of_rooms
        )
    return special_surgery_mapping


def build_remaining_surgery_mapping(
    surgery_list: List[Surgery],
    mapping: Dict[Surgery, List[OperatingRoom]],
    list_of_rooms: List[OperatingRoom],
):
    remainder_mapping = dict()
    surgeries_without_special_requirements = [
        surgery for surgery in surgery_list if not surgery.requirements
    ]
    for surgery in surgeries_without_special_requirements:
        remainder_mapping[surgery] = list_of_rooms
    remainder_mapping.update(mapping)
    return remainder_mapping


def _only_one_available_option(surgery: Surgery, possible_rooms: dict):
    return len(possible_rooms[surgery]) == 1


def assign_special_surgeries(
    surgery_list: List[Surgery], list_of_rooms: List[OperatingRoom]
) -> Dict[Surgery, List[OperatingRoom]]:
    logger.info(
        f"[Assignment] Assigning {len(surgery_list)} surgeries to operating rooms"
    )
    surgeries_with_special_requirements = [
        surgery for surgery in surgery_list if surgery.requirements
    ]
    mapping = find_suitable_rooms_for_special_surgeries(
        surgeries_with_special_requirements, list_of_rooms
    )
    scheduled_surgeries = []
    for surgery in mapping:
        if _only_one_available_option(surgery, mapping):
            mapping[surgery][0].surgeries_to_schedule.append(surgery)
            logger.debug(
                f"[1:1] Assigned surgery {surgery} to room {mapping[surgery][0]}"
            )
            scheduled_surgeries.append(surgery)

    [mapping.pop(surgery) for surgery in scheduled_surgeries]

    mapping = build_remaining_surgery_mapping(surgery_list, mapping, list_of_rooms)
    return mapping


def disperse_surgeries_evenly(
    mapping: Dict[Surgery, List[OperatingRoom]]
):
    logger.info(
        f"[Assignment] Optimization step, assigning remaining {len(mapping)} surgeries to operating rooms"
    )
    surgery_list = list()
    rooms = set()
    for surgery in mapping:
        surgery_list.append(surgery)
        [rooms.add(room) for room in mapping[surgery]]
    distribute_surgeries_to_operating_rooms(surgery_list, list(rooms))


if __name__ == "__main__":
    a = Surgery(name="a", duration_in_minutes=300, requirements=[])
    b = Surgery(name="b", duration_in_minutes=200, requirements=[])
    c = Surgery(name="c", duration_in_minutes=300, requirements=[])
    d = Surgery(name="d", duration_in_minutes=400, requirements=[])
    e = Surgery(name="e", duration_in_minutes=300, requirements=[])
    f = Surgery(name="f", duration_in_minutes=30, requirements=[])
    g = Surgery(name="g", duration_in_minutes=60, requirements=[])
    h = Surgery(name="h", duration_in_minutes=120, requirements=[])

    o = OperatingRoom(id="OR1", properties=["microscope", "xray", "ct"])
    p = OperatingRoom(id="OR2", properties=["microscope", "ct"])
    r = OperatingRoom(id="OR3", properties=["microscope", "ct"])

    # or_list = [o, p, r]
    # surgery_list = [a, b, c, d, e, f, g, h]*10
    surgery_list = [Surgery(name=f"s{i}", duration_in_minutes=60 * ((i % 3) + 1), requirements=[]) for i in range(20)]
    or_list = [OperatingRoom(id=f"o{i}", properties=[]) for i in range(5)]

    remaineder = assign_special_surgeries(surgery_list, or_list)
    disperse_surgeries_evenly(remaineder)
    distribute_surgeries_to_days(or_list)
