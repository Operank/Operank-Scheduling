from typing import List

from .parse_hopital_data import map_surgery_to_team

surgery_to_team_mapping = map_surgery_to_team()


class OperatingRoom:
    def __init__(self, id: str, properties: List[str], uuid: int) -> None:
        self.id = id
        self.properties = properties
        self.timeslots_to_schedule: List[Timeslot] = list()
        self.uuid = uuid

    def __repr__(self) -> str:
        return self.id


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
        self, name: str, duration_in_minutes: int, uuid: int, requirements: List[str] = list()
    ) -> None:
        self.name = name.upper()
        self.duration = duration_in_minutes
        self.requirements = requirements
        self.suitable_teams = surgery_to_team_mapping.get(self.name, [])
        self.uuid = uuid

    def __repr__(self) -> str:
        return f"{self.name} ({self.duration}m)"

    def can_fit_in(self, timeslot: Timeslot) -> bool:
        return self.duration in timeslot
