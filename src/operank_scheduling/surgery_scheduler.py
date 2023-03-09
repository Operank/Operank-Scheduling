# from typing import Dict, List

from ..algo.distribution_models import (
    distribute_timeslots_to_days,
    distribute_timeslots_to_operating_rooms,
)

# from loguru import logger
from .models.operank_models import OperatingRoom, Timeslot

"""
# General Idea
    Take a list of timeslots (w/ their requirements & duration) and a list of rooms (w/ their properties),
    and assign timeslots to rooms, such that:
        1. timeslots that require special requirements get all of their requirements (1:1 relations only)
        2. If multiple rooms satisfy the requirements, or if no special requirements are given,
           assign timeslots to rooms such that the total duration is close to even.
        3. For each room, assign timeslots to days, such that minimum days are required.
"""


# def find_suitable_rooms_for_special_surgeries(
#     list_of_surgeries: List[Surgery], list_of_rooms: List[OperatingRoom]
# ) -> Dict[Surgery, List[OperatingRoom]]:
#     special_surgery_mapping = dict()
#     for surgery in list_of_surgeries:
#         special_surgery_mapping[surgery] = find_suitable_rooms_for_surgery(
#             surgery, list_of_rooms
#         )
#     return special_surgery_mapping


# def build_remaining_surgery_mapping(
#     surgery_list: List[Surgery],
#     mapping: Dict[Surgery, List[OperatingRoom]],
#     list_of_rooms: List[OperatingRoom],
# ):
#     remainder_mapping = dict()
#     surgeries_without_special_requirements = [
#         surgery for surgery in surgery_list if not surgery.requirements
#     ]
#     for surgery in surgeries_without_special_requirements:
#         remainder_mapping[surgery] = list_of_rooms
#     remainder_mapping.update(mapping)
#     return remainder_mapping


# def _only_one_available_option(surgery: Surgery, possible_rooms: dict):
#     return len(possible_rooms[surgery]) == 1


# def assign_special_surgeries(
#     surgery_list: List[Surgery], list_of_rooms: List[OperatingRoom]
# ) -> Dict[Surgery, List[OperatingRoom]]:
#     logger.info(
#         f"[Assignment] Assigning {len(surgery_list)} surgeries to operating rooms"
#     )
#     surgeries_with_special_requirements = [
#         surgery for surgery in surgery_list if surgery.requirements
#     ]
#     mapping = find_suitable_rooms_for_special_surgeries(
#         surgeries_with_special_requirements, list_of_rooms
#     )
#     scheduled_surgeries = []
#     for surgery in mapping:
#         if _only_one_available_option(surgery, mapping):
#             mapping[surgery][0].surgeries_to_schedule.append(surgery)
#             logger.debug(
#                 f"[1:1] Assigned surgery {surgery} to room {mapping[surgery][0]}"
#             )
#             scheduled_surgeries.append(surgery)

#     [mapping.pop(surgery) for surgery in scheduled_surgeries]

#     mapping = build_remaining_surgery_mapping(surgery_list, mapping, list_of_rooms)
#     return mapping


if __name__ == "__main__":
    timeslot_list = [Timeslot(duration=60 * ((i % 3) + 1)) for i in range(16)]
    or_list = [OperatingRoom(id=f"o{i}", properties=[], uuid=i) for i in range(2)]
    distribute_timeslots_to_operating_rooms(timeslot_list, or_list)
    distribute_timeslots_to_days(or_list)
    pass
