from typing import List

from .parse_hopital_data import map_surgery_to_team

surgery_to_team_mapping = map_surgery_to_team()


class OperatingRoom:
    def __init__(self, id: str, properties: List[str]) -> None:
        self.id = id
        self.properties = properties
        self.timeslots_to_schedule: List[Timeslot] = list()

    def __repr__(self) -> str:
        return self.id


class Timeslot:
    def __init__(self, duration: int) -> None:
        self.duration = duration

    def __contains__(self, duration) -> bool:
        return duration <= self.duration

    def __repr__(self) -> str:
        return f"Timeslot ({self.duration})"


class Surgery:
    def __init__(
        self, name: str, duration_in_minutes: int, requirements: List[str] = list()
    ) -> None:
        self.name = name.upper()
        self.duration = duration_in_minutes
        self.requirements = requirements
        self.suitable_teams = surgery_to_team_mapping.get(self.name, [])

    def __repr__(self) -> str:
        return f"{self.name} ({self.duration}m)"

    def can_fit_in(self, timeslot: Timeslot) -> bool:
        return self.duration in timeslot
