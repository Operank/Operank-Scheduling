from nicegui import ui
from typing import List, Callable, Tuple, Union, Dict
from operank_scheduling.models.operank_models import (
    Patient,
    Surgery,
    Surgeon,
    Timeslot,
    OperatingRoom,
    get_operating_room_by_name,
    schedule_patient_to_timeslot,
)
from operank_scheduling.algo.patient_assignment import suggest_feasible_dates
import datetime

AppState = Dict[str, List[Union[Patient, Surgery, OperatingRoom, Surgeon]]]


def fetch_valid_timeslots(patient: Patient, app_state: AppState):
    surgery_list = app_state["surgeries"]
    operating_rooms = app_state["rooms"]
    dates = suggest_feasible_dates(patient, surgery_list, operating_rooms, [])
    return [(date[0].id, date[1], date[2]) for date in dates]


class PatientSchedulingScreen:
    def __init__(
        self, app_state: AppState, patient_index: int, refresh_function: Callable
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
            DateSelectionOptionsRow(
                patient, available_slots, app_state, refresh_function
            )


class DateSelectionOptionsRow:
    def __init__(
        self,
        patient: Patient,
        list_of_slots: List[Tuple[str, datetime.datetime, Timeslot]],
        app_state: AppState,
        update_callback: Callable,
    ) -> None:
        with ui.row():
            for slot in list_of_slots:
                DateSelectionCard(patient, slot, app_state, update_callback)


class DateSelectionCard(ui.card):
    def __init__(
        self,
        patient: Patient,
        slot: Tuple[str, datetime.datetime, Timeslot],
        app_state: AppState,
        update_callback: Callable,
    ):
        super().__init__()
        self.displayed_date = datetime.datetime.strftime(slot[1], "%d/%m/%Y @ %H:%M")
        self.update_callback = update_callback
        self.operating_room_name = slot[0]
        self.patient = patient
        self.slot_date = slot[1]
        self.timeslot = slot[2]
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
        if self.patient.is_scheduled:
            return

        operating_room = get_operating_room_by_name(
            self.operating_room_name, self.app_state["rooms"]
        )
        schedule_patient_to_timeslot(
            self.patient,
            self.slot_date,
            self.timeslot,
            operating_room,
            self.app_state["surgeries"],
        )
        ui.notify(f"Scheduled {self.patient.name} for {self.slot_date}", closeBtn=True)
        self.app_state["patients"].remove(self.patient)
        self.app_state["scheduled_patients"] += 1
        self.classes(add="bg-green-400")
        self.update_callback()

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
            "patients": patient_list,
            "surgeries": surgery_list,
            "rooms": rooms,
            "scheduled_patients": 0,
        }

        self.patients_to_schedule = len(patient_list)
        self.current_patient_idx = 0
        self.display_patient_scheduling_ui()

    def draw_inner_ui(self, app_state: AppState, patient_index: int):
        with self.content.classes("items-center"):
            if self.scheduling_state["scheduled_patients"] == self.patients_to_schedule:
                self.draw_finish_screen()
            else:
                ArrowNavigationControls(direction="left", state_func=self.update_app_state)
                PatientSchedulingScreen(
                    app_state, patient_index, refresh_function=self.update_app_state
                )
                ArrowNavigationControls(direction="right", state_func=self.update_app_state)
                ui.linear_progress(
                    value=(
                        self.scheduling_state["scheduled_patients"]
                        / self.patients_to_schedule
                    ),
                    show_value=False,
                    size="20px",
                )

    def display_patient_scheduling_ui(self):
        self.content.clear()
        self.draw_inner_ui(
            self.scheduling_state,
            self.current_patient_idx % self.patients_to_schedule,
        )

    def update_app_state(self, direction: str = ""):
        if direction == "up":
            self.current_patient_idx += 1
        elif direction == "down":
            self.current_patient_idx -= 1

        self.display_patient_scheduling_ui()

    def draw_finish_screen(self):
        self.content.clear()
        for room in self.scheduling_state["rooms"]:
            with ui.card():
                ui.label(f"Room: {room.id}")
                for day in room.schedule:
                    with ui.card():
                        ui.label(f"Day: {day}")
                        for surgery in room.schedule[day]:
                            ui.label(f"{surgery.name}")
                            ui.label(f"{surgery.duration} minutes")
