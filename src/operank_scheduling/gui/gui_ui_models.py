from nicegui import ui
from typing import List, Callable, Tuple, Union, Dict
from operank_scheduling.models.operank_models import Patient, Surgery, OperatingRoom, get_operating_room_by_name
from operank_scheduling.algo.patient_assignment import suggest_feasible_dates
import datetime

AppState = Dict[str, List[Union[Patient, Surgery, OperatingRoom]]]


def fetch_valid_timeslots(patient: Patient, app_state: AppState):
    surgery_list = app_state["surgeries"]
    operating_rooms = app_state["rooms"]
    feasible_slots = suggest_feasible_dates(
        patient, surgery_list, operating_rooms, []
    )
    return [(slot[0].id, slot[1]) for slot in feasible_slots]


class PatientSchedulingScreen:
    def __init__(
        self, app_state: AppState, patient_index: int
    ) -> None:

        patient = app_state["patients"][patient_index]
        available_slots = fetch_valid_timeslots(patient, app_state)

        with ui.card().classes("m-auto"):
            with ui.card().classes("m-auto"):
                FormattedTextRow(
                    title="Patient:", text=patient.name, icon="personal_injury"
                )
                FormattedTextRow(title="ID:", text=patient.patient_id, icon="badge")
                FormattedTextRow(
                    title="Procedure:",
                    text=patient.surgery_name,
                    icon="health_and_safety",
                )
            DateSelectionOptionsRow(patient, available_slots, app_state)


class DateSelectionOptionsRow:
    def __init__(self, patient: Patient, list_of_slots: List[Tuple[str, datetime.datetime]], app_state: AppState) -> None:
        with ui.row():
            for slot in list_of_slots:
                DateSelectionCard(patient, slot, app_state)


class DateSelectionCard(ui.card):
    def __init__(self, patient: Patient, slot: Tuple[str, datetime.datetime], app_state: AppState):
        super().__init__()
        self.displayed_date = datetime.datetime.strftime(slot[1], "%d/%m/%Y @ %H:%M")
        self.operating_room_name = slot[0]
        self.patient = patient
        self.slot_date = slot[1]
        self.app_state = app_state
        with self:
            col = ui.column()
            with col.classes("items-center"):
                FormattedTextRow(text=self.operating_room_name, icon="location_on")
                FormattedTextRow(text=self.displayed_date, icon="event")

        self.on("click", self.select_slot)
        self.on("mouseover", self.hover_highlight)
        self.on("mouseout", self.hover_unhighlight)

    def select_slot(self):
        operating_room = get_operating_room_by_name(self.operating_room_name, self.app_state["rooms"])
        ui.notify(f"Found {operating_room}")
        ui.notify(f"Scheduled {self.patient.name} for {self.slot_date}", closeBtn=True)

    def hover_highlight(self):
        self.classes(add="bg-blue-400")

    def hover_unhighlight(self):
        self.classes(remove="bg-blue-400")


class FormattedTextRow:
    def __init__(self, title: str = "", text: str = "", icon: str = "") -> None:
        with ui.row().classes("items-center"):
            if icon != "":
                ui.icon(icon)
            ui.label(title).classes("text-weight-bold")
            ui.label(text).classes("text-weight-regular")


class ArrowNavigationControls:
    def __init__(self, direction: str, state_func: Callable) -> None:
        self.state_func = state_func
        with ui.column():
            if direction == "left":
                icon = ui.icon("arrow_back_ios")
                callback = self.prev_cb
            else:
                icon = ui.icon("arrow_forward_ios")
                callback = self.next_cb

        icon.on("click", callback)

    def next_cb(self):
        self.state_func("up")

    def prev_cb(self):
        self.state_func("down")


class PatientSchedulingUI:
    def __init__(
        self,
        patient_list: List[Patient],
        surgery_list: List[Surgery],
        rooms: List[OperatingRoom],
    ) -> None:
        self.content = ui.row()
        self.scheduling_state: AppState = {
            "patients" : patient_list,
            "surgeries" : surgery_list,
            "rooms" : rooms
        }

        self.patients_to_schedule = len(patient_list)
        self.current_patient_idx = 0
        self.display_patient_scheduling_ui()

    def draw_inner_ui(self, app_state: AppState, patient_index: int):
        with self.content.classes("items-center"):
            ArrowNavigationControls(direction="left", state_func=self.update_app_state)
            PatientSchedulingScreen(app_state, patient_index)
            ArrowNavigationControls(direction="right", state_func=self.update_app_state)

    def display_patient_scheduling_ui(self):
        self.content.clear()
        self.draw_inner_ui(
            self.scheduling_state,
            self.current_patient_idx,
        )

    def update_app_state(self, direction: str):
        self.content.clear()
        if direction == "up":
            self.current_patient_idx += 1
        else:
            self.current_patient_idx -= 1

        self.draw_inner_ui(
            self.scheduling_state,
            self.current_patient_idx,
        )
