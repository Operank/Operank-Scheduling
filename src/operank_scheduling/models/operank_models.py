import datetime
from typing import List, Dict, Union, Tuple

from .parse_hopital_data import load_surgeon_data, map_surgery_to_team
from operank_scheduling.models.enums import surgeon_teams

surgery_to_team_mapping = map_surgery_to_team()


class OperatingRoom:
    def __init__(self, id: str, properties: List[str] = []) -> None:
        self.id = id
        self.properties = properties
        self.timeslots_to_schedule: List[Timeslot] = list()
        self.timeslots_by_day: List[List[Timeslot]] = list()
        self.schedule: Dict[datetime.date, List[Union[Timeslot, Surgery]]] = dict()
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


class Patient:
    def __init__(
        self,
        name: str,
        patient_id: str,
        surgery_name: str,
        referrer: str,
        estimated_duration_m: int,
        priority: int,
        phone_number: str,
        uuid: int
    ) -> None:
        self.name = name
        self.patient_id = patient_id
        self.surgery_name = surgery_name
        self.referrer = referrer
        self.duration_m = estimated_duration_m
        self.priority = priority
        self.phone_number = phone_number
        self.uuid = uuid
        self.is_scheduled = False

    def mark_as_done(self):
        self.is_scheduled = True


class Surgery:
    def __init__(
        self,
        name: str,
        duration_in_minutes: int,
        uuid: int,
        patient: Patient,
        requirements: List[str] = list(),
    ) -> None:
        self.name = name.upper()
        self.duration = duration_in_minutes
        self.requirements = requirements
        self.suitable_teams = list()
        self.suitable_wards = list()
        self.patient = patient
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


class Surgeon:
    def __init__(self, name: str, surgeon_id: int, ward: int, team: str) -> None:
        self.name = name
        self.id = surgeon_id
        self.ward = ward
        self.team = team.upper()
        self.availability: Dict[datetime.date, List[List]] = dict()
        self.occupied_times: Dict[datetime.date, List[Tuple[Surgery, datetime.datetime]]] = dict()

    def __repr__(self) -> str:
        return f"{self.name}"

    def is_available_at(self, date: datetime.date):
        return self.availability[date]

    def get_earliest_open_timeslot(self, date: datetime.date, duration_minutes: int) -> Union[datetime.datetime, None]:
        for availability_slot in self.availability[date]:
            window_start_time = datetime.datetime.combine(date, availability_slot[0])
            window_end_time = datetime.datetime.combine(date, availability_slot[1])
            if window_start_time + datetime.timedelta(minutes=duration_minutes) <= window_end_time:
                # This is a good slot, return it but also reduce the slot:
                new_slot_start_time = window_start_time + datetime.timedelta(minutes=duration_minutes)
                availability_slot[0] = new_slot_start_time.time()
                return self, window_start_time
        # Otherwise, this surgeon can not take this operation, so we return None
        return None

    def add_surgery(self, surgery: Surgery, surgery_time: datetime.datetime) -> None:
        date = surgery_time.date()
        self.occupied_times[date].append((surgery, surgery_time))


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


def get_operating_room_by_name(
    name: str, operating_rooms: List[OperatingRoom]
) -> OperatingRoom:
    for operating_room in operating_rooms:
        if operating_room.id == name:
            return operating_room


def replace_timeslot_by_surgery(schedule: List, timeslot: Timeslot, surgery: Surgery):
    index_to_replace = schedule.index(timeslot)
    schedule[index_to_replace] = surgery


def get_surgery_by_name(name: str, surgeries: List[Surgery]):
    for surgery in surgeries:
        if name.upper() == surgery.name.upper():
            return surgery


def schedule_patient_to_timeslot(
    patient: Patient,
    date: datetime.datetime,
    timeslot: datetime.datetime,
    operating_room: OperatingRoom,
    surgeries: List[Surgery],
    surgeon: Surgeon = None,
):
    try:
        surgery = get_surgery_by_name(patient.surgery_name, surgeries)
        replace_timeslot_by_surgery(operating_room.schedule[date], timeslot, surgery)
        patient.mark_as_done()
    except ValueError:
        raise ValueError("Some mismatch found?")
    return True
