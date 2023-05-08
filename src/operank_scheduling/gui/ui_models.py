from loguru import logger

from operank_scheduling.gui.scheduling_page import PatientSchedulingUI
from operank_scheduling.gui.setup_page import SetupPage
from operank_scheduling.gui.summary_page import OperatingRoomScheduleScreen
from operank_scheduling.models.operank_models import (
    get_all_surgeons,
)
from operank_scheduling.models.parse_hopital_data import load_surgeon_schedules
from operank_scheduling.gui.structs import AppState, UIScreen

export_app_state = None


class StateManager:
    def __init__(self) -> None:
        self.app_state = AppState(
            patients=[], timeslots=[], rooms=[], surgeons=[], surgeries=[]
        )
        logger.info("Loading surgeon data...")
        self.app_state.surgeons = get_all_surgeons()
        logger.info("Loading surgeon schedules...")
        load_surgeon_schedules(self.app_state.surgeons)
        self.update_app_state()

    def update_app_state(self):
        if self.app_state.current_screen is UIScreen.SCHEDULING:
            PatientSchedulingUI(self.app_state, self.update_app_state)
        elif self.app_state.current_screen == UIScreen.ROOM_SCHEDULE_DISPLAY:
            OperatingRoomScheduleScreen(self.app_state, self.update_app_state)
        elif self.app_state.current_screen == UIScreen.SETUP:
            SetupPage(self.app_state, self.update_app_state)
