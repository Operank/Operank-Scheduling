from ortools.sat.python import cp_model
from typing import Dict, List, Any
from math import factorial
from loguru import logger

from .algo_helpers import lazy_permute
from models.operating_room import OperatingRoom
from models.surgery import Surgery

MAX_VAL_LIM = 10000


def restructure_data(
    surgeries: List[Surgery], rooms: List[OperatingRoom]
) -> Dict[str, Any]:
    model_data = dict()
    operating_rooms_amt = len(rooms)

    model_data["surgery_durations"] = [surgery.duration for surgery in surgeries]
    model_data["surgeries"] = list(range(len(model_data["surgery_durations"])))
    model_data["rooms"] = list(range(operating_rooms_amt))

    model_data["max_total_duration"] = (
        max(model_data["surgery_durations"])
        * len(model_data["surgery_durations"])
        // operating_rooms_amt
    )

    return model_data


def distribute_surgeries_to_operating_rooms(
    surgeries: List[Surgery], rooms: List[OperatingRoom]
) -> Dict[OperatingRoom, List[Surgery]]:

    data = restructure_data(surgeries, rooms)
    model = cp_model.CpModel()

    # Variables ---------------------------------------------
    # x[i, j] = 1 if surgery i is assigned to room j.
    x = {}
    for i in data["surgeries"]:
        for j in data["rooms"]:
            x[(i, j)] = model.NewIntVar(0, 1, f"x_{i}_{j}")

    absolute_length_differences = [
        model.NewIntVar(0, MAX_VAL_LIM, f"diff_{i}")
        for i in range(factorial(len(data["rooms"])))
    ]
    # End Variables -----------------------------------------

    # Constraints -------------------------------------------
    # Each surgery must be in exactly one room.
    for surgery in data["surgeries"]:
        model.AddExactlyOne(x[surgery, j] for j in data["rooms"])

    def total_room_duration(room):
        return sum(
            [
                x[(surgery, room)] * data["surgery_durations"][surgery]
                for surgery in data["surgeries"]
            ]
        )

    for j in data["rooms"]:
        model.Add(total_room_duration(j) <= data["max_total_duration"])

    def total_room_duration_differences():
        total_room_durations = [total_room_duration(room) for room in data["rooms"]]
        all_perms = lazy_permute(total_room_durations)
        for idx, permutation in enumerate(all_perms):
            temp = model.NewIntVar(
                -MAX_VAL_LIM, MAX_VAL_LIM, f"temp_{idx}"
            )  # temporary variable, as a workaround for abs val
            model.Add(temp == (permutation[0] - permutation[1]))
            model.AddAbsEquality(absolute_length_differences[idx], temp)

    total_room_duration_differences()
    # End Constraints ---------------------------------------

    # Optimization ------------------------------------------
    model.Minimize(sum(absolute_length_differences))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print(f"Total surgeries to schedule: {len(data['surgeries'])}")
        print(f"Optimal difference (lower is better): {solver.ObjectiveValue()}")
        for operating_room_idx in data["rooms"]:
            operating_room = rooms[operating_room_idx]
            total_duration = 0
            for surgery_idx in data["surgeries"]:
                surgery = surgeries[surgery_idx]
                if solver.Value(x[surgery_idx, operating_room_idx]) > 0:
                    operating_room.surgeries_to_schedule.append(surgery)
                    total_duration += surgery.duration

            logger.debug(
                f"Surgeries in {operating_room}: {operating_room.surgeries_to_schedule}"
            )
            logger.debug(
                f"Total queue duration in {operating_room} is {total_duration} [m]"
            )

        logger.debug(f"Solver took {solver.WallTime():.2f} [ms] to finish")
    else:
        logger.warning(
            f"The problem does not have an optimal solution.\n"
            f"The solution status was deemed {solver.StatusName(status)}"
        )


if __name__ == "__main__":
    a = Surgery(name="a", duration_in_minutes=60, requirements=[])
    b = Surgery(name="b", duration_in_minutes=60, requirements=["microscope"])
    c = Surgery(name="c", duration_in_minutes=120, requirements=["microscope", "xray"])
    # d = Surgery(name="d", duration_in_minutes=120, requirements=["microscope", "xray"])

    o = OperatingRoom(id="OR1", properties=["microscope", "xray", "ct"])
    p = OperatingRoom(id="OR2", properties=["microscope", "ct"])

    or_list = [o, p]
    surgery_list = [a, b, c]

    distribute_surgeries_to_operating_rooms(surgery_list, or_list)
