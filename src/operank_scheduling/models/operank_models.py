from typing import List


class OperatingRoom:
    def __init__(self, id: str, properties: List[str]) -> None:
        self.id = id
        self.properties = properties
        self.surgeries_to_schedule: List[Surgery] = list()

    def __repr__(self) -> str:
        return self.id


class Surgery:
    def __init__(
        self, name: str, duration_in_minutes: int, requirements: List[str]
    ) -> None:
        self.name = name
        self.duration = duration_in_minutes
        self.requirements = requirements

    def __repr__(self) -> str:
        return f"{self.name} ({self.duration}m)"
