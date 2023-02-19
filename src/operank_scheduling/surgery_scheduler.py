from typing import List, Tuple
from models.operating_room import OperatingRoom
from models.surgery import Surgery
from algo.algo_helpers import intersection_size

"""
# General Idea
    Take a list of surgeries (w/ their requirements & duration) and a list of rooms (w/ their properties),
    and assign surgeries to rooms, such that:
        1. Surgeries that require special requirements get all of their requirements (1:1 relations only)
        2. If multiple rooms satisfy the requirements, or if no special requirements are given,
           assign surgeries to rooms such that the total duration is close to even.
        3. For each room, assign surgeries to days, such that minimum days are required.
"""

def find_suitable_rooms_for_surgery(surgery: Surgery, list_of_rooms: List[OperatingRoom]) -> List:
    assert surgery.requirements
    suitable_rooms = []
    for room in list_of_rooms:
        match_strength = intersection_size(surgery.requirements, room.properties)
        if match_strength >= len(surgery.requirements):
            suitable_rooms.append(room)
    return suitable_rooms


def find_suitable_rooms_for_special_surgeries(list_of_surgeries: List[Surgery], list_of_rooms: List[OperatingRoom]) -> dict:
    special_surgery_mapping = dict()
    for surgery in list_of_surgeries:
        special_surgery_mapping[surgery.name] = find_suitable_rooms_for_surgery(surgery, list_of_rooms)
    return special_surgery_mapping


def assign_special_surgeries(surgery_list: List[Surgery], list_of_rooms: List[OperatingRoom]):
    surgeries_with_special_requirements = [surgery for surgery in surgery_list if surgery.requirements]
    mapping = find_suitable_rooms_for_special_surgeries(surgeries_with_special_requirements, list_of_rooms)
    return mapping


def disperse_surgeries_evenly():
    pass

if __name__ == "__main__":
    a = Surgery(name="a", duration_in_minutes=60, requirements=[])
    b = Surgery(name="b", duration_in_minutes=60, requirements=["microscope"])
    c = Surgery(name="c", duration_in_minutes=60, requirements=["microscope", "xray"])

    o = OperatingRoom(id="OR1", properties=["microscope", "xray", "ct"])
    p = OperatingRoom(id="OR2", properties=["microscope", "ct"])

    or_list = [o, p]
    surgery_list = [a, b, c]

    res = assign_special_surgeries(surgery_list, or_list)
    print(res)