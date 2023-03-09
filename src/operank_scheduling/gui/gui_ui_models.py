from nicegui import ui
from typing import List, Callable
from operank_scheduling.models.operank_models import Patient, Surgery, OperatingRoom
from operank_scheduling.algo.patient_assignment import suggest_feasible_dates
import datetime


class PatientSchedulingScreen:
    def __init__(
        self, patient: Patient, suggested_dates: List[datetime.datetime]
    ) -> None:
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
            DateSelectionOptionsRow(suggested_dates)


class DateSelectionOptionsRow:
    def __init__(self, list_of_dates: List[datetime.datetime]) -> None:
        with ui.row():
            for idx, date in enumerate(list_of_dates):
                DateSelectionCard(date, option_index=idx)


class DateSelectionCard(ui.card):
    def __init__(self, date_and_time: datetime.datetime, option_index: int):
        super().__init__()
        self.displayed_date = datetime.datetime.strftime(
            date_and_time, "%d/%m/%Y @ %H:%M"
        )
        self.option_index = option_index
        with self:
            col = ui.column()
            with col.classes("items-center"):
                ui.label(self.displayed_date)
            self.on("click", self.button_cb)
            self.on("mouseover", self.highlight)
            self.on("mouseout", self.unhighlight)

    def button_cb(self):
        ui.notify(self.option_index, closeBtn=True)
        return self.option_index

    def highlight(self):
        self.classes(add="bg-blue-400")

    def unhighlight(self):
        self.classes(remove="bg-blue-400")


class FormattedTextRow:
    def __init__(self, title: str, text: str, icon: str = "") -> None:
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
        ui.notify("Moving to next patient", closeBtn=True)
        self.state_func("up")

    def prev_cb(self):
        ui.notify("Moving to previous patient", closeBtn=True)
        self.state_func("down")


class PatientSchedulingUI:
    def __init__(
        self,
        patient_list: List[Patient],
        surgery_list: List[Surgery],
        rooms: List[OperatingRoom],
    ) -> None:
        self.content = ui.row()
        self.patient_list = patient_list
        self.surgery_list = surgery_list
        self.rooms = rooms

        self.current_patient_idx = 0
        self.datetimes_list = self.fetch_valid_timeslots()
        self.display_patient_scheduling_ui()

    def fetch_valid_timeslots(self):
        patient = self.patient_list[self.current_patient_idx % len(self.patient_list)]
        feasible_slots = suggest_feasible_dates(
            patient, self.surgery_list, self.rooms, []
        )
        return [slot[1] for slot in feasible_slots]

    def draw_inner_ui(self, patient, datetimes_list):
        with self.content.classes("items-center"):
            ArrowNavigationControls(direction="left", state_func=self.update_app_state)
            self.patient_state = PatientSchedulingScreen(patient, datetimes_list)
            ArrowNavigationControls(direction="right", state_func=self.update_app_state)

    def display_patient_scheduling_ui(self):
        self.content.clear()
        self.draw_inner_ui(
            self.patient_list[self.current_patient_idx % len(self.patient_list)],
            self.datetimes_list,
        )

    def update_app_state(self, direction: str):
        self.content.clear()
        if direction == "up":
            self.current_patient_idx += 1
        else:
            self.current_patient_idx -= 1
        self.datetimes_list = self.fetch_valid_timeslots()
        self.draw_inner_ui(
            self.patient_list[self.current_patient_idx % len(self.patient_list)],
            self.datetimes_list,
        )
