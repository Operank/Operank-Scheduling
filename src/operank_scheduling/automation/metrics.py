from typing import List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from operank_scheduling.models.operank_models import get_surgery_by_patient

from operank_scheduling.models.operank_models import Patient, Surgery
from loguru import logger

workday_length_minutes = 480


def get_average_utilization(path):
    system_output = pd.read_excel(path)
    system_output["Duration"] = system_output["End Time"] - system_output["Start Time"]

    dates = system_output["Date"].unique()
    dfs = []
    utilization_avg = []
    for date in dates:
        daily_schedule = system_output[system_output["Date"] == date]
        daily_utilization = daily_schedule.groupby("OR")["Duration"].sum()
        daily_utilization = daily_utilization.apply(
            lambda x: (x.seconds / 60) / workday_length_minutes
        )
        utilization_avg.append(daily_utilization.mean())
        dfs.append(daily_utilization)

    return np.mean(utilization_avg)


def get_days_used(path):
    system_output = pd.read_excel(path)
    return len(system_output["Date"].unique())


def get_priority_adherence(
    patient_list: List[Patient], surgery_list: List[Surgery]
) -> Tuple[np.ndarray, np.ndarray]:
    priorities_per_date = dict()
    for patient in patient_list:
        surgery = get_surgery_by_patient(patient, surgery_list)
        try:
            try:
                priorities_per_date[surgery.scheduled_time.date()].append(
                    patient.priority
                )
            except Exception:
                priorities_per_date[surgery.scheduled_time.date()] = [patient.priority]
        except Exception:
            logger.debug("This patient wasn't scheduled in this run...")
    sorted_dates = sorted(list(priorities_per_date.keys()))
    average_priority_per_date = []
    full_date_axis = []
    full_priority_axis = []
    for date in sorted_dates:
        amt_of_scheduled_surgeries = len(priorities_per_date[date])
        full_date_axis.extend([date] * amt_of_scheduled_surgeries)
        full_priority_axis.extend(priorities_per_date[date])
        average_priority_per_date.append(np.mean(priorities_per_date[date]))
    return sorted_dates, average_priority_per_date, full_date_axis, full_priority_axis
