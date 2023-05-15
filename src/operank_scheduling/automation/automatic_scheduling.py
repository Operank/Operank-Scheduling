import datetime
from random import choice
import pandas as pd

from loguru import logger

from operank_scheduling.algo.patient_assignment import (
    sort_patients_by_priority,
    suggest_feasible_dates,
)
from operank_scheduling.algo.surgery_distribution_models import (
    perform_preliminary_scheduling,
)
from operank_scheduling.models.io_utilities import find_project_root
from operank_scheduling.models.operank_models import get_all_surgeons
from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
    load_patients_from_excel,
)
from operank_scheduling.models.parse_hopital_data import load_surgeon_schedules
from operank_scheduling.models.operank_models import (
    get_operating_room_by_name,
    schedule_patient_to_timeslot,
    Timeslot,
)


# Export
def export_schedule_as_excel(operating_rooms, filepath=None):
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
    for room in operating_rooms:
        for day in room.schedule:
            for event in room.schedule[day]:
                if isinstance(event, Timeslot):
                    continue
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
    if filepath is not None:
        df.to_excel(f"{filepath}", sheet_name="OR Schedule")
    else:
        df.to_excel("Exported_Schedule.xlsx", sheet_name="OR Schedule")


root_dir = find_project_root()
export_dir = root_dir / "validation"
num_runs = 5

for automation_index in range(num_runs):
    # Load surgeons
    logger.info("Loading surgeon data...")
    surgeon_list = get_all_surgeons()
    logger.info("Loading surgeon schedules...")
    load_surgeon_schedules(surgeon_list)



    # Load patients from file
    patients_file = root_dir / "assets" / "test_30.xlsx"
    operating_room_file = root_dir / "assets" / "example_operating_room_schedule.json"
    patient_list, surgery_list, timeslot_list = load_patients_from_excel(patients_file)
    operating_rooms = load_operating_rooms_from_json(operating_room_file, mode="path")
    patient_list = sort_patients_by_priority(patient_list)

    # TODO: Consider adding timeslots here
    timeslot_list.extend([Timeslot(360), Timeslot(180), Timeslot(90), Timeslot(120)])
    logger.warning("Added extra timeslots!!!!")

    # Do preliminary scheduling
    perform_preliminary_scheduling(timeslot_list, operating_rooms)
    for room in operating_rooms:
        room.schedule_timeslots_to_days(datetime.datetime.now().date())

    for idx, patient in enumerate(patient_list):
        logger.info(f"Scheduling patient {idx + 1}/{len(patient_list)}")
        timeslots_data = suggest_feasible_dates(
            patient, surgery_list, operating_rooms, surgeon_list
        )
        if timeslots_data is None:
            logger.critical(f"Failed to schedule ❌")
            continue
        selected_timeslot = choice(timeslots_data)
        room = selected_timeslot[0]
        best_slot = selected_timeslot[1]
        timeslot = selected_timeslot[2]
        surgeon_name = selected_timeslot[3]
        operating_room = get_operating_room_by_name(room.id, operating_rooms)
        schedule_patient_to_timeslot(
            patient,
            best_slot,
            timeslot,
            operating_room,
            surgery_list,
            surgeon_name,
            surgeon_list,
        )
        logger.info(f"Scheduled patient {idx + 1} at {best_slot}")

    export_schedule_as_excel(
        operating_rooms, export_dir / f"automated_schedule_{automation_index + 1}.xlsx"
    )
    logger.info("Exported schedule ✅")
