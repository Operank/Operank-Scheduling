import datetime
from typing import Callable

import pandas as pd
from nicegui import ui

from operank_scheduling.gui.structs import AppState
from operank_scheduling.models.operank_models import OperatingRoom


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
            ui.button("Export to Excel", on_click=export_schedule_as_excel)


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
    df.sort_values(by=["Date"], inplace=True)
    df.to_excel("Exported_Schedule.xlsx", sheet_name="OR Schedule")
    ui.notify("Exported the schedule successfully! 🚀")
