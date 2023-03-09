from nicegui import ui
from typing import List, Callable
from operank_scheduling.models.operank_models import Patient
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
            with ui.column().classes("items-center"):
                ui.label(self.displayed_date)
                ui.button("Select", on_click=self.button_cb)

    def button_cb(self):
        ui.notify(self.option_index, closeBtn=True)
        return self.option_index


class FormattedTextRow:
    def __init__(self, title: str, text: str, icon: str = "") -> None:
        with ui.row().classes("items-center"):
            if icon != "":
                ui.icon(icon)
            ui.label(title).classes("text-weight-bold")
            ui.label(text).classes("text-weight-regular")


class PatientNavigationControls:
    def __init__(self, state_func: Callable) -> None:
        self.state_func = state_func
        with ui.row():
            ui.button(text="Previous Patient", on_click=self.prev_cb)
            ui.button(text="Next Patient", on_click=self.next_cb)

    def next_cb(self):
        ui.notify("Moving to next patient", closeBtn=True)
        self.state_func("up")

    def prev_cb(self):
        ui.notify("Moving to previous patient", closeBtn=True)
        self.state_func("down")


class PatientSchedulingUI:
    def __init__(self, patient_list: List[Patient], datetimes_list) -> None:
        self.content = ui.column()
        self.current_patient_idx = 0
        self.patient_list = patient_list
        self.datetimes_list = datetimes_list
        self.display_patient_scheduling_ui()

    def draw_inner_ui(self, patient, datetimes_list):
        with self.content.classes("items-center"):
            self.patient_state = PatientSchedulingScreen(patient, datetimes_list)
            PatientNavigationControls(self.update_app_state)

    def display_patient_scheduling_ui(self):
        self.content.clear()
        self.draw_inner_ui(
            self.patient_list[self.current_patient_idx], self.datetimes_list
        )

    def update_app_state(self, direction: str):
        self.content.clear()
        if direction == "up":
            self.current_patient_idx += 1
        else:
            self.current_patient_idx -= 1
        self.draw_inner_ui(
            self.patient_list[self.current_patient_idx], self.datetimes_list
        )
