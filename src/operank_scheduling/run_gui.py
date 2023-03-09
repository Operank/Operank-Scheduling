from nicegui import ui
import datetime
from gui.gui_ui_models import PatientSchedulingUI
from gui.static_ui_elements import OperankHeader
from operank_scheduling.models.operank_models import get_all_surgeons
from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
    load_patients_from_json,
)
from operank_scheduling.models.io_utilities import find_project_root

datetimes_list = [
    datetime.datetime.now(),
    datetime.datetime.now() + datetime.timedelta(days=1),
    datetime.datetime.now() + datetime.timedelta(days=13),
]

assets_dir = find_project_root() / "assets"
patient_list, surgery_list, timeslot_list = load_patients_from_json(
    assets_dir / "example_patient_data.json"
)
operating_rooms = load_operating_rooms_from_json(
    assets_dir / "example_operating_room_schedule.json"
)
surgeons = get_all_surgeons()

OperankHeader()
PatientSchedulingUI(patient_list, datetimes_list)
ui.footer()

ui.run(title="Operank", favicon=str(assets_dir / "operank_favicon.jpg"))
