from enum import Enum, auto
from typing import List

from nicegui import ui

from operank_scheduling.models.operank_models import (
    OperatingRoom,
    Patient,
    Surgeon,
    Surgery,
    Timeslot,
)


class UIScreen(Enum):
    SETUP = auto()
    SCHEDULING = auto()
    ROOM_SCHEDULE_DISPLAY = auto()


class AppState:
    def __init__(
        self,
        patients: List[Patient],
        timeslots: List[Timeslot],
        rooms: List[OperatingRoom],
        surgeons: List[Surgeon],
        surgeries: List[Surgery],
    ) -> None:
        self.timeslots = timeslots
        self.patients = patients
        self.rooms = rooms
        self.surgeons = surgeons
        self.surgeries = surgeries
        self.current_screen = UIScreen.SETUP
        self.num_scheduled_patients = 0
        self.canvas = ui.column().classes("m-auto")
        self.current_patient_idx = 0
        self.start_date = None
