import datetime
from typing import Callable, List, Tuple

from nicegui import ui
from loguru import logger

from operank_scheduling.algo.patient_assignment import suggest_feasible_dates
from operank_scheduling.gui.theme import AppTheme
from operank_scheduling.gui.structs import AppState, UIScreen
from operank_scheduling.models.operank_models import (
    Patient,
    Surgeon,
    Timeslot,
    get_operating_room_by_name,
    schedule_patient_to_timeslot,
)


def fetch_valid_timeslots(patient: Patient, app_state: AppState):
    surgery_list = app_state.surgeries
    operating_rooms = app_state.rooms
    surgeons = app_state.surgeons
    timeslots_data = suggest_feasible_dates(
        patient, surgery_list, operating_rooms, surgeons
    )
    if timeslots_data is None:
        return None
    return [(slot[0].id, slot[1], slot[2], slot[3]) for slot in timeslots_data]


class PatientSchedulingScreen:
    def __init__(self, app_state: AppState, refresh_function: Callable) -> None:
        patient = app_state.patients[
            app_state.current_patient_idx % len(app_state.patients)
        ]
        available_slots = fetch_valid_timeslots(patient, app_state)
        if available_slots is None:
            patient.is_skipped = True
            logger.debug(f"Skipping patient {patient.name}")
            app_state.current_patient_idx += 1
            refresh_function("reset")

        with ui.card().classes("m-auto").style("max-width: 1200px; min-width: 1000px"):
            with ui.card().classes("m-auto w-full"):
                with ui.row().classes("w-full m-auto justify-between"):
                    with ui.column().classes("m-auto"):
                        FormattedTextRow(
                            title="Patient:", text=patient.name, icon="personal_injury"
                        )
                        FormattedTextRow(
                            title="ID:", text=patient.patient_id, icon="badge"
                        )
                        FormattedTextRow(
                            title="Procedure:",
                            text=patient.surgery_name,
                            icon="health_and_safety",
                        )
                    with ui.column().classes("m-auto"):
                        FormattedTextRow(
                            title="Priority:",
                            text=patient.priority,
                            icon="low_priority",
                        )
                        FormattedTextRow(
                            title="Phone Number:",
                            text=patient.phone_number,
                            icon="call",
                        )
            DateSelectionOptionsRow(
                patient, available_slots, app_state, refresh_function
            )


class DateSelectionOptionsRow:
    def __init__(
        self,
        patient: Patient,
        list_of_slots: List[Tuple[str, datetime.datetime, Timeslot, Surgeon]],
        app_state: AppState,
        update_callback: Callable,
    ) -> None:
        with ui.row().classes("m-auto"):
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
        self.surgeon_name = slot[3]
        self.app_state = app_state
        with self:
            col = ui.column()
            with col.classes("items-center"):
                FormattedTextRow(text=self.operating_room_name, icon="location_on")
                FormattedTextRow(text=self.displayed_date, icon="event")
                FormattedTextRow(text=self.surgeon_name, icon="medication")

        self.on("click", self.select_slot)
        self.on("mouseover", self.hover_highlight)
        self.on("mouseout", self.hover_unhighlight)

    def select_slot(self):
        if self.patient.is_scheduled:
            return

        operating_room = get_operating_room_by_name(
            self.operating_room_name, self.app_state.rooms
        )
        schedule_patient_to_timeslot(
            self.patient,
            self.slot_date,
            self.timeslot,
            operating_room,
            self.app_state.surgeries,
            self.surgeon_name,
            self.app_state.surgeons,
        )
        ui.notify(
            f"Scheduled {self.patient.name} for {self.slot_date}",
            closeBtn=True,
            position="bottom-right",
        )
        self.patient.mark_as_done()
        self.app_state.num_scheduled_patients += 1
        self.classes(add="bg-green-400")
        self.update_callback("reset")

    def hover_highlight(self):
        self.classes(add="bg-blue-400")

    def hover_unhighlight(self):
        self.classes(remove="bg-blue-400")


class FormattedTextRow:
    def __init__(self, title: str = "", text: str = "", icon: str = "") -> None:
        with ui.row().classes("items-center"):
            if icon != "":
                ui.icon(icon).style(AppTheme.big_text)
            ui.label(title).classes("text-weight-bold").style(AppTheme.big_text)
            ui.label(text).classes("text-weight-regular").style(AppTheme.medium_text)


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
    def __init__(self, app_state: AppState, state_update_cb: Callable) -> None:
        self.app_state = app_state
        app_state.canvas.clear()
        self.state_update_cb = state_update_cb
        self.patients_to_schedule = len(self.app_state.patients)
        self.display_patient_scheduling_ui()

    def draw_inner_ui(self, app_state: AppState):
        with self.app_state.canvas.classes("items-center"):
            done_patients = [
                1
                for patient in self.app_state.patients
                if (patient.is_scheduled or patient.is_skipped)
            ]
            if sum(done_patients) == self.patients_to_schedule:
                self.app_state.current_screen = UIScreen.ROOM_SCHEDULE_DISPLAY
                self.state_update_cb()
            else:
                # Find patient that wasn't scheduled
                for index, patient in enumerate(self.app_state.patients):
                    if not (patient.is_scheduled or patient.is_skipped):
                        break
                self.app_state.current_patient_idx = index
                with ui.row():
                    ArrowNavigationControls(
                        direction="left", state_func=self.update_app_state
                    )
                    PatientSchedulingScreen(
                        app_state, refresh_function=self.update_app_state
                    )
                    ArrowNavigationControls(
                        direction="right", state_func=self.update_app_state
                    )
                ui.linear_progress(
                    value=(
                        self.app_state.num_scheduled_patients
                        / self.patients_to_schedule
                    ),
                    show_value=False,
                    size="30px",
                ).classes(add="rounded")

    def display_patient_scheduling_ui(self):
        self.app_state.canvas.clear()
        try:
            self.draw_inner_ui(self.app_state)
        except Exception as e:
            logger.warning(f"❌ {e} : [TODO: Address skips correctly in GUI]")

    def update_app_state(self, direction: str = "reset"):
        if direction == "up":
            self.app_state.current_patient_idx += 1
        elif direction == "down":
            self.app_state.current_patient_idx -= 1
        elif direction == "reset":
            pass

        self.display_patient_scheduling_ui()
