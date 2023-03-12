import os
from nicegui import ui
import datetime
from gui.gui_ui_models import StateManager, AppState
from gui.static_ui_elements import OperankHeader
from operank_scheduling.models.operank_models import get_all_surgeons
from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
    load_patients_from_json,
)
from operank_scheduling.models.io_utilities import find_project_root
from operank_scheduling.algo.surgery_distribution_models import (
    perform_preliminary_scheduling,
)
from operank_scheduling.algo.patient_assignment import sort_patients_by_priority


assets_dir = find_project_root() / "assets"
patient_list, surgery_list, timeslot_list = load_patients_from_json(
    assets_dir / "example_patient_data.json"
)
operating_rooms = load_operating_rooms_from_json(
    assets_dir / "example_operating_room_schedule.json"
)
patient_list = sort_patients_by_priority(patient_list)
surgeons = get_all_surgeons()
operating_rooms = operating_rooms[:2]
perform_preliminary_scheduling(timeslot_list, operating_rooms)

for operating_room in operating_rooms:
    operating_room.schedule_timeslots_to_days(datetime.datetime.now().date())

app_state = AppState(patient_list, operating_rooms, surgeons, surgery_list)

OperankHeader()
StateManager(app_state)
ui.footer()

os.environ["MATPLOTLIB"] = "false"
ui.run(title="Operank", favicon=str(assets_dir / "operank_favicon.jpg"))
