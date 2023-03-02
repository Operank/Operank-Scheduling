from typing import Dict, List
from csv import reader

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
