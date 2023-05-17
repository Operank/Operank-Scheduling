import datetime
import glob
import os
import warnings
from random import choice

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger

from operank_scheduling.algo.patient_assignment import (
    sort_patients_by_priority_and_duration,
    suggest_feasible_dates,
)
from operank_scheduling.algo.surgery_distribution_models import (
    perform_preliminary_scheduling,
)
from operank_scheduling.automation.metrics import (
    get_average_utilization,
    get_days_used,
    get_priority_adherence,
)
from operank_scheduling.models.io_utilities import find_project_root
from operank_scheduling.models.operank_models import (
    Timeslot,
    get_all_surgeons,
    get_operating_room_by_name,
    schedule_patient_to_timeslot,
)
from operank_scheduling.models.parse_data_to_models import (
    load_operating_rooms_from_json,
    load_patients_from_excel,
)
from operank_scheduling.models.parse_hopital_data import load_surgeon_schedules


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
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=FutureWarning)
                    df = df.append(surgery_data, ignore_index=True)
    df.sort_values(by=["Date"], inplace=True)
    if filepath is not None:
        df.to_excel(f"{filepath}", sheet_name="OR Schedule")
    else:
        df.to_excel("Exported_Schedule.xlsx", sheet_name="OR Schedule")


root_dir = find_project_root()
export_dir = root_dir / "validation"
priority_x_axes = list()
priority_y_axes = list()
full_x = list()
full_y = list()


def run_automation_cycle(automation_index: int):
    failed_to_schedule = 0
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
    patient_list = sort_patients_by_priority_and_duration(patient_list)

    # TODO: Consider adding timeslots here
    timeslot_list.extend(
        [
            Timeslot(180),
            # Timeslot(180),
            # Timeslot(180),
            # Timeslot(180),
            # Timeslot(180),
            # Timeslot(180),
            Timeslot(120),
            # Timeslot(120),
            # Timeslot(120),
            # Timeslot(120),
            # Timeslot(120),
            # Timeslot(120),
            Timeslot(60),
            # Timeslot(60),
            # Timeslot(60),
            # Timeslot(60),
        ]
    )
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
            logger.critical(
                f"Failed to schedule patient {idx + 1} who had a priority of {patient.priority}❌"
            )
            failed_to_schedule += 1
        else:
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
        operating_rooms,
        export_dir / f"automated_schedule_{automation_index + 1}.xlsx",
    )
    logger.info("Exported schedule ✅")

    priority_x, priority_y, full_x_out, full_y_out = get_priority_adherence(patient_list, surgery_list)
    priority_x_axes.append(priority_x)
    priority_y_axes.append(priority_y)
    full_x.append(full_x_out)
    full_y.append(full_y_out)

    if failed_to_schedule:
        logger.info(f"Failed to schedule {failed_to_schedule} patients 😢")
    return failed_to_schedule


if __name__ == "__main__":
    num_runs = 2

    root_dir / "validation/*"
    # Remove previous contents of dir:
    logger.info("Removing past results... 🧹")
    file_list = glob.glob("validation/*")
    for filepath in file_list:
        os.remove(filepath)

    failiure_vec = list()
    for automation_index in range(num_runs):
        amt_failed_to_schedule = run_automation_cycle(automation_index)
        failiure_vec.append(amt_failed_to_schedule)
    file_list = glob.glob("validation/*")

    utilization_data = dict()
    days_used = dict()

    logger.info(
        f"Average amount of patients we failed to schedule is: {np.mean(failiure_vec)}"
    )

    for result_index, path in enumerate(file_list):
        utilization_data[result_index] = get_average_utilization(path)
        days_used[result_index] = get_days_used(path)

    total_mean_utilization = np.mean(list(utilization_data.values()))
    mean_days_used = np.mean(list(days_used.values()))
    logger.info(
        f"Mean utilization over all runs: {total_mean_utilization:.2f}, "
        f"Distribution per run: {list(utilization_data.values())}"
    )
    logger.info(
        f"Mean days used: {mean_days_used:.2f}, "
        f"Distribution per run: {list(days_used.values())}"
    )

    for index, axes in enumerate(zip(priority_x_axes, priority_y_axes)):
        plt.plot(*axes, label=f"Run #{index + 1}")
    for index, axes in enumerate(zip(full_x, full_y)):
        plt.scatter(*axes, label=f"Run #{index + 1}")
    plt.legend()
    plt.show()
    pass
