from nicegui import ui, events
from typing import List, Callable, Tuple
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
from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
    load_patients_from_json,
)
from operank_scheduling.algo.patient_assignment import sort_patients_by_priority
from operank_scheduling.algo.surgery_distribution_models import (
    perform_preliminary_scheduling,
)
from operank_scheduling.models.operank_models import get_all_surgeons
from operank_scheduling.models.parse_hopital_data import load_surgeon_schedules
from operank_scheduling.gui.ui_tables import display_patient_table

from .theme import AppTheme
import datetime
from enum import Enum, auto
import pandas as pd
from loguru import logger


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


def fetch_valid_timeslots(patient: Patient, app_state: AppState):
    surgery_list = app_state.surgeries
    operating_rooms = app_state.rooms
    surgeons = app_state.surgeons
    timeslots_data = suggest_feasible_dates(
        patient, surgery_list, operating_rooms, surgeons
    )
    return [(slot[0].id, slot[1], slot[2], slot[3]) for slot in timeslots_data]


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


class SetupPage:
    def __init__(self, app_state: AppState, update_cb: Callable) -> None:
        self.callback = update_cb
        self.is_patient_data_complete = False
        self.is_room_data_complete = False
        self.app_state = app_state
        with self.app_state.canvas.classes("items-center"):
            with ui.row():
                with ui.card():
                    ui.label("Attach patients to be scheduled")
                    ui.upload(on_upload=self.handle_patient_file_upload).props(
                        "accept=.xlsx, .csv, .json"
                    ).classes("max-w-full")

                with ui.card():
                    ui.label("Attach operating room schedule")
                    ui.upload(on_upload=self.handle_operating_room_upload).props(
                        "accept=.xlsx, .csv, .json"
                    ).classes("max-w-full")
            with ui.row():
                ui.button("Schedule!", on_click=self.check_ready).classes(add="disabled")

    def handle_patient_file_upload(
        self, upload_event: events.UploadEventArguments
    ) -> None:
        file_content = upload_event.content.read().decode("utf-8")
        patient_list, surgery_list, timeslot_list = load_patients_from_json(
            file_content, mode="stream"
        )
        patient_list = sort_patients_by_priority(patient_list)
        self.app_state.patients = patient_list
        self.app_state.surgeries = surgery_list
        self.app_state.timeslots = timeslot_list
        logger.info(f"Data of {len(patient_list)} patients recieved!")
        with self.app_state.canvas.classes("items-center"):
            display_patient_table(self.app_state.patients)
        self.is_patient_data_complete = True

    def handle_operating_room_upload(
        self, upload_event: events.UploadEventArguments
    ) -> None:
        file_content = upload_event.content.read().decode("utf-8")
        self.app_state.rooms = load_operating_rooms_from_json(
            file_content, mode="stream"
        )[:2]
        logger.info(f"Data of {len(self.app_state.rooms)} operating rooms recieved!")
        self.is_room_data_complete = True

    def check_ready(self):
        if self.is_room_data_complete and self.is_patient_data_complete:
            scheduling_button.classes(remove="disabled")
            logger.info("Scheduling... ")
            perform_preliminary_scheduling(
                self.app_state.timeslots, self.app_state.rooms
            )

            for room in self.app_state.rooms:
                room.schedule_timeslots_to_days(datetime.datetime.now().date())

            logger.info("Moving to scheduling phase")
            self.app_state.current_screen = UIScreen.SCHEDULING
            self.callback()


class PatientSchedulingScreen(StateManager):
    def __init__(
        self, app_state: AppState, patient_index: int, refresh_function: Callable
    ) -> None:
        patient = app_state.patients[patient_index]
        available_slots = fetch_valid_timeslots(patient, app_state)

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
        ui.notify(f"Scheduled {self.patient.name} for {self.slot_date}", closeBtn=True)
        self.app_state.patients.remove(self.patient)
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

    def draw_inner_ui(self, app_state: AppState, patient_index: int):
        with self.app_state.canvas.classes("items-center"):
            if self.app_state.num_scheduled_patients == self.patients_to_schedule:
                self.app_state.current_screen = UIScreen.ROOM_SCHEDULE_DISPLAY
                self.state_update_cb()
            else:
                with ui.row():
                    ArrowNavigationControls(
                        direction="left", state_func=self.update_app_state
                    )
                    PatientSchedulingScreen(
                        app_state, patient_index, refresh_function=self.update_app_state
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
        self.draw_inner_ui(
            self.app_state,
            self.app_state.current_patient_idx % self.patients_to_schedule,
        )

    def update_app_state(self, direction: str = ""):
        if direction == "up":
            self.app_state.current_patient_idx += 1
        elif direction == "down":
            self.app_state.current_patient_idx -= 1
        elif direction == "reset":
            self.app_state.current_patient_idx = 0

        self.display_patient_scheduling_ui()


class RoomSchedule:
    def __init__(self, room: OperatingRoom):
        table_cols = [
            {
                "name": "date",
                "label": "Date",
                "field": "date",
                "align": "left",
                "sortable": True,
            },
            {"name": "start", "label": "Start Time", "field": "start", "align": "left"},
            {"name": "end", "label": "End Time", "field": "end", "align": "left"},
            {
                "name": "surgeon",
                "label": "Surgeon",
                "field": "surgeon",
                "align": "left",
            },
            {
                "name": "patient",
                "label": "Patient",
                "field": "patient",
                "align": "left",
            },
            {
                "name": "procedure",
                "label": "Surgery",
                "field": "procedure",
                "align": "left",
            },
        ]
        rows = []
        for day in room.schedule:
            daily_rows = []
            for surgery in room.schedule[day]:
                surgery_end_time = surgery.scheduled_time + datetime.timedelta(
                    minutes=surgery.duration
                )
                daily_rows.append(
                    {
                        "date": f"{day}",
                        "start": f"{surgery.scheduled_time.time()}",
                        "end": f"{surgery_end_time.time()}",
                        "surgeon": f"{surgery.surgeon}",
                        "patient": f"{surgery.patient.name}",
                        "procedure": f"{surgery.name}",
                    }
                )
            daily_rows.sort(key=lambda x: x["start"])
            rows += daily_rows
        ui.table(columns=table_cols, rows=rows, row_key="name", title=f"{room.id}")


class OperatingRoomScheduleScreen:
    def __init__(self, app_state: AppState, update_interface_cb: Callable) -> None:
        global export_app_state
        self.app_state = app_state
        self.app_state.canvas.clear()
        with self.app_state.canvas.classes("items-center"):
            for room in self.app_state.rooms:
                with ui.card():
                    RoomSchedule(room)
            export_app_state = self.app_state
            ui.button(
                "Export to Excel", on_click=export_schedule_as_excel
            )


def export_schedule_as_excel():
    global export_app_state
    df = pd.DataFrame(
        columns=[
            "Date",
            "Start Time",
            "End Time",
            "OR",
            "Patient ID",
            "Patient Name",
            "Surgery",
            "Surgeon",
        ]
    )
    for room in export_app_state.rooms:
        for day in room.schedule:
            for event in room.schedule[day]:
                patient = event.patient
                surgery_data = {
                    "Date": day,
                    "Start Time": event.scheduled_time,
                    "End Time": event.scheduled_time
                    + datetime.timedelta(minutes=event.duration),
                    "OR": room.id,
                    "Patient ID": patient.patient_id,
                    "Patient Name": patient.name,
                    "Surgery": patient.surgery_name,
                    "Surgeon": event.surgeon,
                }
                df = df.append(surgery_data, ignore_index=True)
    df.sort_values(by=['Date'], inplace=True)
    df.to_excel("Exported_Schedule.xlsx", sheet_name="OR Schedule")
    ui.notify("Exported the schedule successfully! 🚀")
