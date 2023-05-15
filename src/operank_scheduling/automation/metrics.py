import pandas as pd
import numpy as np

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
    system_output["Duration"] = system_output["End Time"] - system_output["Start Time"]
    return len(system_output["Date"].unique())
