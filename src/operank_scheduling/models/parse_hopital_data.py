from csv import reader
from typing import Dict, List

import pandas as pd

from .io_utilities import find_project_root

project_root = find_project_root()


def _skip_header_row(iterator):
    next(iterator, None)


def parse_team_strings_to_list(suitable_teams: str) -> List:
    return [team.strip() for team in suitable_teams.split(",")]


def map_surgery_to_team() -> Dict[str, List]:
    mapping_file = project_root / "assets" / "surgery_to_team_mapping.csv"
    mapping = dict()
    with open(mapping_file, "r") as rfp:
        file_iter = reader(rfp)
        _skip_header_row(file_iter)
        for row in file_iter:
            mapping[row[0].upper()] = parse_team_strings_to_list(row[1])
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
