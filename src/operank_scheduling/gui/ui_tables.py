from nicegui import ui
from typing import List
from operank_scheduling.models.operank_models import Patient


def display_patient_table(patients: List[Patient]):
    table_cols = [
        {
            "name": "name",
            "label": "Patient Name",
            "field": "name",
            "align": "left",
            "sortable": True,
        },
        {"name": "id", "label": "ID", "field": "id", "align": "left"},
        {"name": "surgery", "label": "Surgery", "field": "surgery", "align": "left"},
        {
            "name": "priority",
            "label": "Priority",
            "field": "priority",
            "align": "left",
            "sortable": True,
        },
    ]
    rows = []
    for patient in patients:
        rows.append(
            {
                "name": f"{patient.name}",
                "id": f"{patient.patient_id}",
                "surgery": f"{patient.surgery_name}",
                "priority": f"{patient.priority}",
            }
        )
    return ui.table(
        columns=table_cols, rows=rows, row_key="name", title="Patients List"
    )
