import datetime
from typing import List, Dict

from .parse_hopital_data import load_surgeon_data, map_surgery_to_team
from src.operank_scheduling.models.enums import surgeon_teams

surgery_to_team_mapping = map_surgery_to_team()


class OperatingRoom:
    def __init__(self, id: str, properties: List[str] = []) -> None:
        self.id = id
        self.properties = properties
        self.timeslots_to_schedule: List[Timeslot] = list()
        self.timeslots_by_day: List[List[Timeslot]] = list()
        self.schedule: Dict[datetime.date, List[Timeslot]] = dict()
        self.non_working_days = [4, 5]  # 4: Friday, 5: Saturday

    def __repr__(self) -> str:
        return self.id

    def add_non_working_days(self, days_to_add: List[int]):
        for day in days_to_add:
            if day not in self.non_working_days:
                self.non_working_days.append(day)

    def _get_next_working_days(
        self, current_day: datetime.date, days_to_generate: int
    ) -> List[datetime.date]:
        workdays = list()
        generated_days = 0
        while generated_days < days_to_generate:
            while current_day.weekday() in self.non_working_days:
                # Skip weekends
                current_day = current_day + datetime.timedelta(days=1)
            workdays.append(current_day.date())

            # Move to the following day
            current_day = current_day + datetime.timedelta(days=1)
            generated_days += 1
        return workdays

    def schedule_timeslots_to_days(self, starting_day_date: datetime.date):
        starting_day_datetime = datetime.datetime(
            year=starting_day_date.year,
            month=starting_day_date.month,
            day=starting_day_date.day,
        )

        working_days = self._get_next_working_days(
            starting_day_datetime, len(self.timeslots_by_day)
        )

        for day_idx, day in enumerate(working_days):
            self.schedule[day] = self.timeslots_by_day[day_idx]


class Timeslot:
    bins = [30, 60, 120, 180, 360, 480]

    def __init__(self, duration: int) -> None:
        self.duration = self.get_appropriate_bin(duration)

    def __contains__(self, duration) -> bool:
        return duration <= self.duration

    def __repr__(self) -> str:
        return f"Timeslot ({self.duration})"

    def get_appropriate_bin(self, duration):
        for bin in self.bins:
            if duration <= bin:
                return bin
        raise IndexError("Surgery is too long - no appropriate bin found")


class Surgery:
    def __init__(
        self,
        name: str,
        duration_in_minutes: int,
        uuid: int,
        requirements: List[str] = list(),
    ) -> None:
        self.name = name.upper()
        self.duration = duration_in_minutes
        self.requirements = requirements
        self.suitable_teams = list()
        self.suitable_wards = list()
        self.uuid = uuid

        self.assign_team_or_ward()

    def __repr__(self) -> str:
        return f"{self.name} ({self.duration}m)"

    def can_fit_in(self, timeslot: Timeslot) -> bool:
        return self.duration in timeslot

    def assign_team_or_ward(self):
        suitable_teams = surgery_to_team_mapping.get(self.name, [])
        for value in suitable_teams:
            if value.upper() in surgeon_teams:
                self.suitable_teams.append(value.upper())
            else:
                self.suitable_wards.append(int(value))


class Patient:
    def __init__(
        self,
        name: str,
        patient_id: str,
        surgery_name: str,
        referrer: str,
        estimated_duration_m: int,
        priority: int,
        uuid: int,
    ) -> None:
        self.name = name
        self.patient_id = patient_id
        self.surgery_name = surgery_name
        self.referrer = referrer
        self.duration_m = estimated_duration_m
        self.priority = priority
        self.uuid = uuid


class Surgeon:
    def __init__(self, name: str, surgeon_id: int, ward: int, team: str) -> None:
        self.name = name
        self.id = surgeon_id
        self.ward = ward
        self.team = team.upper()
        self.occupied_times = list()


def get_all_surgeons() -> List[Surgeon]:
    surgeons_list = list()
    surgeon_data_list = load_surgeon_data()
    for surgeon_data in surgeon_data_list:
        name = surgeon_data["name"]
        surgeon_id = surgeon_data["surgeon_id"]
        ward = surgeon_data["ward"]
        team = surgeon_data["team"]
        surgeons_list.append(
            Surgeon(name=name, surgeon_id=surgeon_id, ward=ward, team=team)
        )
    return surgeons_list
