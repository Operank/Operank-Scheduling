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


def parse_single_json_block(patient_data: str) -> Tuple[Patient, Surgery, Timeslot]:
    global auto_id
    p_data = json.loads(patient_data)
    name = p_data["name"]
    patient_id = p_data["patient_id"]
    surgery_name = p_data["surgery_name"].upper()
    referrer = p_data["referrer"].upper()
    estimated_duration_m = p_data["estimated_duration_m"]
    priority = p_data["priority"]

    patient = Patient(
        name=name,
        patient_id=patient_id,
        surgery_name=surgery_name,
        referrer=referrer,
        estimated_duration_m=estimated_duration_m,
        priority=priority,
        uuid=auto_id
    )

    surgery = Surgery(
        name=surgery_name,
        duration_in_minutes=estimated_duration_m,
        uuid=auto_id
    )

    timeslot = Timeslot(duration=estimated_duration_m)
    auto_id += 1

    return patient, surgery, timeslot
