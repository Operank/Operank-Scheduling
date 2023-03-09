from nicegui import ui
from typing import List
from operank_scheduling.models.operank_models import Patient
import datetime


class PatientSchedulingScreen:
    def __init__(self, patient: Patient, suggested_dates: List[datetime.datetime]) -> None:
        with ui.column().classes('m-auto'):
            with ui.card().classes('m-auto'):
                ui.label(patient.name)
                ui.label(patient.patient_id)
                ui.label(patient.surgery_name)
            DateSelectionOptionsRow(suggested_dates)


class DateSelectionOptionsRow:
    def __init__(self, list_of_dates: List[datetime.datetime]) -> None:
        with ui.row():
            for date in list_of_dates:
                DateSelectionCard(date)


class DateSelectionCard(ui.card):
    def __init__(self, date_and_time: datetime.datetime):
        super().__init__()
        self.displayed_date = datetime.datetime.strftime(
            date_and_time, "%d/%m/%Y @ %H:%M"
        )
        with self:
            with ui.column().classes('items-center'):
                ui.label(self.displayed_date)
                ui.button("Select")

        self.on("dragover.prevent", self.highlight)
        self.on("dragleave", self.unhighlight)

    def highlight(self) -> None:
        self.classes(add="bg-gray-400")

    def unhighlight(self) -> None:
        self.classes(remove="bg-gray-400")
