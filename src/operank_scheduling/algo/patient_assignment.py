from typing import List
from src.operank_scheduling.models.operank_models import Patient


def sort_patients_by_priority(patient_list: List[Patient]) -> List[Patient]:
    return sorted(patient_list, key=lambda p: p.priority)


def suggest_possible_dates(patients: List[Patient]):
    """
    Sort patients by priority, and then for each patient:
        1. Find which surgery is required and it's duration, along with the required person, team or teams to perform
        2. Find (3?) dates in which the required personnel are available
        3. Find ORs that are active in these days that also have an available timeslot
        4. Display these dates on the GUI (for now, just output)
    """
    pass
