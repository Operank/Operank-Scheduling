import datetime
from typing import Callable

from loguru import logger
from nicegui import events, ui

from operank_scheduling.algo.patient_assignment import sort_patients_by_priority_and_duration
from operank_scheduling.algo.surgery_distribution_models import (
    perform_preliminary_scheduling,
)
from operank_scheduling.gui.structs import AppState, UIScreen
from operank_scheduling.gui.ui_tables import display_patient_table
from operank_scheduling.models.operank_models import Timeslot
from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
    load_patients_from_json,
    load_patients_from_excel,
)


class SetupPage:
    def __init__(self, app_state: AppState, update_cb: Callable) -> None:
        self.callback = update_cb
        self.is_patient_data_complete = False
        self.is_room_data_complete = False
        self.app_state = app_state
        self.patients_table = ui.column().classes("m-auto")
        with self.app_state.canvas.classes("items-center"):
            ui.label("Please attach patient data and operating room data below.")
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

            ui.label(
                "When both files have been uploaded, press the button to start scheduling 🚀"
            )
            with ui.row():
                ui.button("Schedule!", on_click=self.check_ready)

    def handle_patient_file_upload(
        self, upload_event: events.UploadEventArguments
    ) -> None:
        if upload_event.name.split(".")[-1] == "xlsx":
            file_content = upload_event.content.read()
            patient_list, surgery_list, timeslot_list = load_patients_from_excel(
                file_content
            )
        elif upload_event.name.split(".")[-1] == "json":
            file_content = upload_event.content.read().decode("utf-8")
            patient_list, surgery_list, timeslot_list = load_patients_from_json(
                file_content, mode="stream"
            )
        timeslot_list.extend(
            [Timeslot(360), Timeslot(180), Timeslot(90), Timeslot(120)]
        )
        logger.warning("Added extra timeslots!!!!")
        patient_list = sort_patients_by_priority_and_duration(patient_list)
        self.app_state.patients = patient_list
        self.app_state.surgeries = surgery_list
        self.app_state.timeslots = timeslot_list
        logger.info(f"Data of {len(patient_list)} patients recieved!")
        with self.app_state.canvas.classes("items-center"):
            self.patients_table.clear()
            with self.patients_table:
                display_patient_table(self.app_state.patients)
        self.is_patient_data_complete = True

    def handle_operating_room_upload(
        self, upload_event: events.UploadEventArguments
    ) -> None:
        file_content = upload_event.content.read().decode("utf-8")
        self.app_state.rooms = load_operating_rooms_from_json(
            file_content, mode="stream"
        )
        logger.info(f"Data of {len(self.app_state.rooms)} operating rooms recieved!")
        self.is_room_data_complete = True

    def check_ready(self):
        if self.is_room_data_complete and self.is_patient_data_complete:
            logger.info("Scheduling... ")
            with self.app_state.canvas.classes("items-center"):
                self.patients_table.clear()
                ui.spinner(size='5em')
            perform_preliminary_scheduling(
                self.app_state.timeslots, self.app_state.rooms
            )

            for room in self.app_state.rooms:
                room.schedule_timeslots_to_days(datetime.datetime.now().date())

            logger.info("Moving to scheduling phase")
            self.app_state.current_screen = UIScreen.SCHEDULING
            self.callback()
        else:
            missing_files = []
            if not self.is_room_data_complete:
                missing_files.append("OR Schedule")
            if not self.is_patient_data_complete:
                missing_files.append("Patient Data")
            missing_text = ", ".join(missing_files)
            ui.notify(f"Please upload {missing_text}")
