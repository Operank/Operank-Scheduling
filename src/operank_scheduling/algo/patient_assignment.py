from typing import List, Tuple

from loguru import logger
import datetime
from ..algo.algo_helpers import intersection_size

from ..models.operank_models import (
    OperatingRoom,
    Patient,
    Surgeon,
    Surgery,
    Timeslot,
    get_all_surgeons,
)

from random import choice

from ..models.parse_hopital_data import load_surgeon_schedules


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

        else:
            logger.warning(
                f"Allocated random surgeon for {procedure.name}, no suitable surgeons found"
            )
            return [choice(surgeons)]

    return suitable_surgeons


def find_suitable_timeslots(
    procedure: Surgery,
    suitable_rooms: List[OperatingRoom],
    suitable_surgeons: List[Surgeon],
):
    suitable_timeslots = list()
    for room in suitable_rooms:
        # Go over each room
        for day in room.schedule:
            # Look at each day
            for event in room.schedule[day]:
                # Check if the day has empty timeslots that we can schedule in
                if isinstance(event, Timeslot):
                    # For an empty timeslot:
                    #   1. Check that the timeslot is long enough for the procedure
                    if procedure.can_fit_in(event):
                        #   2. Check that one of the suitable surgeons is free to operate
                        earliest_surgeon_timeslots = list()
                        for surgeon in suitable_surgeons:
                            if surgeon.is_available_at(day):
                                earliest_timeslot = surgeon.get_earliest_open_timeslot(
                                    day, procedure.duration
                                )
                                if earliest_timeslot is not None:
                                    # Surgeon has an empty spot for the procedure
                                    earliest_surgeon_timeslots.append(earliest_timeslot)
                            continue
                        if len(earliest_surgeon_timeslots) > 0:
                            earliest_surgeon_timeslots.sort(key=lambda x: x[1])
                            # Add three good options to the pool for this date:
                            if len(earliest_surgeon_timeslots) >= 3:
                                for i in range(3):
                                    (
                                        selected_surgeon,
                                        best_slot,
                                    ) = earliest_surgeon_timeslots[i]
                                    suitable_timeslots.append(
                                        (room, best_slot, event, selected_surgeon.name)
                                    )
                            else:
                                (
                                    selected_surgeon,
                                    best_slot,
                                ) = earliest_surgeon_timeslots[0]
                                suitable_timeslots.append(
                                    (room, best_slot, event, selected_surgeon.name)
                                )

    # Check if we can get 3 options for minimal timeslots
    if len(suitable_timeslots) == 0:
        logger.warning(f"Failed to schedule surgery {procedure}")
    else:
        minimal_timeslot = min(suitable_timeslots, key=lambda x: x[2].duration)
        suitable_minimal_timeslots = [
            timeslot
            for timeslot in suitable_timeslots
            if timeslot[2].duration == minimal_timeslot[2].duration
        ]

        if len(suitable_minimal_timeslots) > 2:
            return suitable_minimal_timeslots[:3]
        else:
            return suitable_timeslots[:3]


def suggest_feasible_dates(
    patient: Patient,
    surgeries: List[Surgery],
    rooms: List[OperatingRoom],
    surgeons: List[Surgeon],
) -> List[Tuple[OperatingRoom, datetime.date, Timeslot]]:
    procedure = get_surgery_by_patient(patient, surgeries)
    suitable_rooms = find_suitable_operating_rooms(procedure, rooms)
    suitable_surgeons = find_suitable_surgeons(procedure, surgeons)
    suitable_timeslots = find_suitable_timeslots(
        procedure, suitable_rooms, suitable_surgeons
    )
    return suitable_timeslots


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
    load_surgeon_schedules(surgeons)

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
