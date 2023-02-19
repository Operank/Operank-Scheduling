from typing import List

class Surgery():
    def __init__(self, name: str, duration_in_minutes: int, requirements: List[str]) -> None:
        self.name = name
        self.duration = duration_in_minutes
        self.requirements = requirements
    
    def __repr__(self) -> str:
        return f"{self.name}({self.duration}m)"