import json
from typing import Tuple, List

from operank_scheduling.models.operank_models import (
    Patient,
    Surgery,
    Timeslot,
    OperatingRoom,
)

from .enums import weekdays_to_numbers

"""
Read patient data given in the format:
{
    "name" : str,
    "patient_id": str,
    "surgery_name" : str,
    "referrer" : str,
    "estimated_duration_m" : int,
    "priority" : int
}

Into surgeries, patients and timeslots.
To link the surgeries and patients, assign uuid.
"""

auto_id = 0


def parse_single_json_block(patient_data: dict) -> Tuple[Patient, Surgery, Timeslot]:
    global auto_id
    name = patient_data["name"]
    patient_id = patient_data["patient_id"]
    surgery_name = patient_data["surgery_name"].upper()
    referrer = patient_data["referrer"].upper()
    estimated_duration_m = patient_data["estimated_duration_m"]
    priority = patient_data["priority"]

    patient = Patient(
        name=name,
        patient_id=patient_id,
        surgery_name=surgery_name,
        referrer=referrer,
        estimated_duration_m=estimated_duration_m,
        priority=priority,
        uuid=auto_id,
    )

    surgery = Surgery(
        name=surgery_name,
        duration_in_minutes=estimated_duration_m,
        uuid=auto_id,
        patient=Patient,
    )

    timeslot = Timeslot(duration=estimated_duration_m)
    auto_id += 1

    return patient, surgery, timeslot


def load_patients_from_json(
    jsonpath: str,
) -> Tuple[List[Patient], List[Surgery], List[Timeslot]]:
    patients = list()
    surgeries = list()
    timeslots = list()

    with open(jsonpath, "r") as json_fp:
        all_patients = json.load(json_fp)
    full_patient_data = all_patients["patients"]

    for single_patient_data in full_patient_data:
        patient, surgery, timeslot = parse_single_json_block(single_patient_data)
        patients.append(patient)
        surgeries.append(surgery)
        timeslots.append(timeslot)

    return patients, surgeries, timeslots


def find_non_working_days_for_operating_room(schedule: dict) -> List[int]:
    non_working_days = list(range(0, 7))
    working_days = list(schedule.keys())

    for day in working_days:
        day_value = weekdays_to_numbers[day]
        non_working_days.remove(day_value)
    return non_working_days


def parse_operating_room_json_to_model(operating_room_data: str) -> OperatingRoom:
    operating_room = OperatingRoom(id=operating_room_data["id"])
    non_working_day_list = find_non_working_days_for_operating_room(
        operating_room_data["schedule"]
    )
    operating_room.add_non_working_days(non_working_day_list)
    return operating_room


def load_operating_rooms_from_json(jsonpath: str) -> List[OperatingRoom]:
    operating_rooms = list()
    with open(jsonpath, "r") as json_fp:
        loaded_operating_rooms = json.load(json_fp)
    loaded_operating_rooms = loaded_operating_rooms["operating_rooms"]
    for room in loaded_operating_rooms:
        operating_rooms.append(parse_operating_room_json_to_model(room))
    return operating_rooms
