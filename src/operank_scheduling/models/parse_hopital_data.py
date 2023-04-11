from typing import Dict, List
import datetime
import pandas as pd

from .io_utilities import find_project_root

project_root = find_project_root()


def parse_team_strings_to_list(suitable_teams: str) -> List:
    return [team.strip() for team in suitable_teams.split(",")]


def map_surgery_to_team() -> Dict[str, List]:
    mapping_file = project_root / "assets" / "surgery_to_team_mapping.csv"
    mapping = dict()
    surgery_map = pd.read_csv(mapping_file)
    for row in surgery_map.iterrows():
        content = row[1]
        mapping[content[0].upper()] = parse_team_strings_to_list(str(content[1]))
    return mapping


def get_surgeon_team(surgeon_data: pd.Series):
    team = "not_assigned"
    available_teams = ["Breast", "Procto", "bariatric", "Robotic"]
    for team_name in available_teams:
        if surgeon_data[1][team_name] == 1:
            team = team_name
    return team.upper()


def load_surgeon_data() -> List[Dict]:
    surgeons = list()
    surgeon_data = project_root / "assets" / "surgeon_team_mapping.csv"
    surgeon_df = pd.read_csv(surgeon_data)

    for series in surgeon_df.iterrows():
        team = get_surgeon_team(series)
        surgeon_data = series[1]
        surgeons.append(
            {
                "name": surgeon_data["Name"],
                "surgeon_id": surgeon_data["ID"],
                "ward": surgeon_data["Ward"],
                "team": team,
            }
        )
    return surgeons


def map_rows_to_days(schedule: pd.DataFrame) -> Dict[datetime.datetime, List]:
    days_to_rows = dict()
    dates = schedule.iloc[1:, 0].dropna()
    indices = list(dates.index)
    for index, day in enumerate(dates):
        day_str = dates.iloc[index]
        day_datetime = datetime.datetime.strptime(day_str, "%d/%m/%Y")
        days_to_rows[day_datetime] = indices[index: index + 2]
    return days_to_rows


def map_row_indices_to_hours() -> Dict[int, datetime.time]:
    hour = 8
    index_to_time = dict()
    # TODO: Consider not-hardcoding-this
    for index in range(1, 24, 2):
        index_to_time[index] = datetime.time(hour=hour, minute=0, second=0)
        index_to_time[index + 1] = datetime.time(hour=hour, minute=30, second=0)
        hour += 1
    return index_to_time


def find_daily_work_hours(schedule: pd.DataFrame, index_to_time_LUT: dict, column_idx: int):
    work_arrangement = list(schedule.iloc[:, column_idx].fillna(0).astype(int))
    today_work_hours = list()
    prev = 0
    start = None
    stop = None
    for index, value in enumerate(work_arrangement):
        current = value
        if current == 1 and prev == 0:
            start = index_to_time_LUT[index + 1]
        if current == 0 and prev == 1:
            stop = index_to_time_LUT[index + 1]
        if (start is not None) and (stop is not None):
            today_work_hours.append((start, stop))
            start = None
            stop = None
        prev = current
    return today_work_hours


def load_surgeon_schedules(surgeons: List) -> None:
    surgeon_schedule_csv = project_root / "assets" / "surgeon_availability.csv"
    schedule_df = pd.read_csv(surgeon_schedule_csv)
    amt_surgeons = len(surgeons)

    # Sort surgeons by ID
    surgeons.sort(key=lambda x: x.id)
    days_to_rows = map_rows_to_days(schedule_df)
    index_to_time = map_row_indices_to_hours()

    for day in list(days_to_rows.keys())[:-1]:
        rows = days_to_rows[day]
        day_schedule = schedule_df.iloc[rows[0] : rows[1], :]

        for column_index in range(3, 3 + amt_surgeons):
            surgeon_idx = column_index - 3  # Column indices are offset from surgeon index by 3
            surgeon_daily_schedule = find_daily_work_hours(day_schedule, index_to_time, column_index)
            surgeons[surgeon_idx].availability[day] = surgeon_daily_schedule
    pass
