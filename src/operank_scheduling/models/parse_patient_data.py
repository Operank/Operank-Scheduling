import json
from typing import Tuple

from src.operank_scheduling.models.operank_models import Patient, Surgery, Timeslot

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
        name=surgery_name, duration_in_minutes=estimated_duration_m, uuid=auto_id
    )

    timeslot = Timeslot(duration=estimated_duration_m)
    auto_id += 1

    return patient, surgery, timeslot


def load_patients_from_json(jsonpath: str):
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
