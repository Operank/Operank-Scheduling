from typing import List

from src.operank_scheduling.models.operank_models import (
    OperatingRoom,
    Patient,
    Surgeon,
    Surgery,
    get_all_surgeons,
)


def sort_patients_by_priority(patient_list: List[Patient]) -> List[Patient]:
    return sorted(patient_list, key=lambda p: p.priority)


def get_surgery_by_patient(patient: Patient, surgeries: List[Surgery]) -> Surgery:
    for surgery in surgeries:
        if surgery.uuid == patient.uuid:
            return surgery
    raise ValueError("Failed to match surgery to patient with UUID")


def suggest_feasible_dates(
    patient: Patient,
    surgeries: List[Surgery],
    rooms: List[OperatingRoom],
    surgeons: List[Surgeon],
) -> List:
    procedure = get_surgery_by_patient(patient, surgeries)
    print(procedure)


def schedule_patients(
    patients: List[Patient], surgeries: List[Surgery], rooms: List[OperatingRoom]
):
    """
    Sort patients by priority, and then for each patient:
        1. Find which surgery is required and it's duration, along with the required person, team or teams to perform
        2. Find (3?) dates in which the required personnel are available
        3. Find ORs that are active in these days that also have an available timeslot
        4. Display these dates on the GUI (for now, just output)
    """
    surgeons = get_all_surgeons()
    sorted_patients = sort_patients_by_priority(patients)
    for patient in sorted_patients:
        dates = suggest_feasible_dates(patient, surgeries, rooms, surgeons)
        print(dates)
    pass
