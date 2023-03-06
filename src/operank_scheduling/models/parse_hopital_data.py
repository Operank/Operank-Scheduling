from typing import Dict, List

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
