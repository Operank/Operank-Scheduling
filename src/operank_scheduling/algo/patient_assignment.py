from typing import List

from loguru import logger
from src.operank_scheduling.algo.algo_helpers import intersection_size

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


def get_surgeons_by_team(team_name: str, surgeons: List[Surgeon]) -> List[Surgeon]:
    matching_surgeons = list()
    for surgeon in surgeons:
        if team_name.upper() == surgeon.team:
            matching_surgeons.append(surgeon)
    return matching_surgeons


def find_suitable_operating_rooms(
    procedure: Surgery, rooms: List[OperatingRoom]
) -> List[OperatingRoom]:
    suitable_rooms = []
    for room in rooms:
        match_strength = intersection_size(procedure.requirements, room.properties)
        if match_strength >= len(procedure.requirements):
            suitable_rooms.append(room)
    return suitable_rooms


def find_suitable_surgeons(
    procedure: Surgery, surgeons: List[Surgeon]
) -> List[Surgeon]:
    suitable_surgeons = list()
    schedule_by_ward = False

    if len(procedure.suitable_teams) == 0:
        schedule_by_ward = True

    for surgeon in surgeons:
        if schedule_by_ward and surgeon.ward in procedure.suitable_wards:
            suitable_surgeons.append(surgeon)

        elif surgeon.team in procedure.suitable_teams:
            suitable_surgeons.append(surgeon)
    return suitable_surgeons


def suggest_feasible_dates(
    patient: Patient,
    surgeries: List[Surgery],
    rooms: List[OperatingRoom],
    surgeons: List[Surgeon],
) -> List:
    dates = list()
    procedure = get_surgery_by_patient(patient, surgeries)
    suitable_rooms = find_suitable_operating_rooms(procedure, rooms)
    suitable_surgeons = find_suitable_surgeons(procedure, surgeons)
    print(procedure, suitable_rooms, suitable_surgeons)
    return dates


def schedule_patients(
    patients: List[Patient], surgeries: List[Surgery], rooms: List[OperatingRoom]
):
    """
    Sort patients by priority, and then for each patient:
        1. Find which surgery is required and it's duration, along with the required person, team or teams to perform
        2. Find ORs that are active in these days that also have an available timeslot
        3. Find (3?) dates in which the required personnel are available
        4. Display these dates on the GUI (for now, just output)
    """
    surgeons = get_all_surgeons()
    sorted_patients = sort_patients_by_priority(patients)
    for patient in sorted_patients:
        logger.debug(f"Now scheduling {patient.name}")
        dates = suggest_feasible_dates(patient, surgeries, rooms, surgeons)
        print(dates)
    pass


if __name__ == "__main__":
    patients = [Patient(uuid=i) for i in range(10)]
    surgeries = [Surgery(uuid=i) for i in range(10)]
    rooms = [OperatingRoom() for i in range(2)]
    schedule_patients(patients, surgeries, rooms)
