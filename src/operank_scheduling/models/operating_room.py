from typing import List
from models.surgery import Surgery


class OperatingRoom:
    def __init__(self, id: str, properties: List[str]) -> None:
        self.id = id
        self.properties = properties
        self.surgeries_to_schedule: List[Surgery] = list()

    def __repr__(self) -> str:
        return self.id
