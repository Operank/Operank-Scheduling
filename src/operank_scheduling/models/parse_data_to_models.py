import json
import pandas as pd
from typing import Tuple, List

from operank_scheduling.models.operank_models import (
    Patient,
    Surgery,
    Timeslot,
    OperatingRoom,
)

from .enums import weekdays_to_numbers
from operank_scheduling.prediction.surgery_duration_estimation import estimate_surgery_durations

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
    phone_number = patient_data["phone_number"]
    priority = patient_data["priority"]

    patient = Patient(
        name=name,
        patient_id=patient_id,
        surgery_name=surgery_name,
        referrer=referrer,
        estimated_duration_m=estimated_duration_m,
        priority=priority,
        phone_number=phone_number,
        uuid=auto_id,
    )

    surgery = Surgery(
        name=surgery_name,
        duration_in_minutes=estimated_duration_m,
        uuid=auto_id,
        patient=patient,
    )

    timeslot = Timeslot(duration=estimated_duration_m)
    auto_id += 1

    return patient, surgery, timeslot


def load_patients_from_json(
    jsonpath: str, mode="path"
) -> Tuple[List[Patient], List[Surgery], List[Timeslot]]:
    patients = list()
    surgeries = list()
    timeslots = list()

    if mode == "path":
        with open(jsonpath, "r") as json_fp:
            all_patients = json.load(json_fp)
    elif mode == "stream":
        all_patients = json.loads(jsonpath)
    full_patient_data = all_patients["patients"]
    patient_data_df = pd.DataFrame.from_dict(full_patient_data)
    full_patient_data = estimate_surgery_durations(patient_data_df)  # Add estimated duration based on ML model

    for single_patient_data in full_patient_data:
        patient, surgery, timeslot = parse_single_json_block(single_patient_data)
        patients.append(patient)
        surgeries.append(surgery)
        timeslots.append(timeslot)

    return patients, surgeries, timeslots


def load_patients_from_excel(
    excelpath: str,
) -> Tuple[List[Patient], List[Surgery], List[Timeslot]]:
    patients = list()
    surgeries = list()
    timeslots = list()
    df = pd.read_excel(excelpath)
    df = estimate_surgery_durations(df)  # Add estimated duration based on ML model

    for _, row in df.iterrows():
        patient_data = {
            "name": row["Name"],
            "patient_id": row["ID"],
            "surgery_name": row["Surgery"],
            "referrer": row["Referrer"],
            "estimated_duration_m": row["estimated_duration_m"],
            "phone_number": row["Phone"],
            "priority": row["Priority"],
        }
        patient, surgery, timeslot = parse_single_json_block(patient_data)
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


def load_operating_rooms_from_json(jsonpath: str, mode="path") -> List[OperatingRoom]:
    operating_rooms = list()
    if mode == "path":
        with open(jsonpath, "r") as json_fp:
            loaded_operating_rooms = json.load(json_fp)
    elif mode == "stream":
        loaded_operating_rooms = json.loads(jsonpath)
    loaded_operating_rooms = loaded_operating_rooms["operating_rooms"]
    for room in loaded_operating_rooms:
        operating_rooms.append(parse_operating_room_json_to_model(room))
    return operating_rooms
