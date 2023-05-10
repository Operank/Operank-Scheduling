from ortools.sat.python import cp_model

from typing import Dict, List, Any
from loguru import logger

from .algo_helpers import lazy_permute
from .intermediate_solutions_cb import SurgeryToRoomSolutionCallback

from ..models.operank_models import OperatingRoom, Timeslot


MAX_VAL_LIM = 10000


def restructure_data(
    timeslots: List[Timeslot], rooms: List[OperatingRoom]
) -> Dict[str, Any]:
    model_data = dict()
    operating_rooms_amt = len(rooms)

    model_data["timeslot_durations"] = [timeslot.duration for timeslot in timeslots]
    model_data["timeslots"] = list(range(len(model_data["timeslot_durations"])))
    model_data["rooms"] = list(range(operating_rooms_amt))
    model_data["num_premutations"] = len(lazy_permute(model_data["rooms"]))

    model_data["max_total_duration"] = (
        max(model_data["timeslot_durations"])
        * len(model_data["timeslot_durations"])
        // operating_rooms_amt
    )

    return model_data


def distribute_timeslots_to_operating_rooms(
    timeslots: List[Timeslot], rooms: List[OperatingRoom]
) -> Dict[OperatingRoom, List[Timeslot]]:
    data = restructure_data(timeslots, rooms)
    model = cp_model.CpModel()

    # Variables ---------------------------------------------
    # x[i, j] = 1 if surgery i is assigned to room j.
    x = {}
    for i in data["timeslots"]:
        for j in data["rooms"]:
            x[(i, j)] = model.NewIntVar(0, 1, f"x_{i}_{j}")
    # End Variables -----------------------------------------

    # Constraints -------------------------------------------
    # Each surgery must be in exactly one room.
    for surgery in data["timeslots"]:
        model.AddExactlyOne(x[surgery, j] for j in data["rooms"])

    def total_room_duration(room):
        return sum(
            [
                x[(surgery, room)] * data["timeslot_durations"][surgery]
                for surgery in data["timeslots"]
            ]
        )

    for j in data["rooms"]:
        model.Add(total_room_duration(j) <= data["max_total_duration"])

    abs_losses = []

    def total_room_duration_differences():
        total_room_durations = [total_room_duration(room) for room in data["rooms"]]
        all_perms = lazy_permute(total_room_durations)
        for idx, permutation in enumerate(all_perms):
            difference = model.NewIntVar(
                0, data["max_total_duration"], f"diff_{idx}"
            )  # temporary variable, as a workaround for abs val
            model.Add(permutation[0] - permutation[1] <= difference)
            model.Add(permutation[1] - permutation[0] <= difference)
            abs_losses.append(difference)

    total_room_duration_differences()
    # End Constraints ---------------------------------------

    # Optimization ------------------------------------------
    model.Minimize(sum(abs_losses))
    solver = cp_model.CpSolver()
    solution_cb = SurgeryToRoomSolutionCallback(data, timeslots, rooms, x)
    solver.parameters.enumerate_all_solutions = True
    # solver.parameters.max_time_in_seconds = 10.0 * 60
    solver.parameters.max_time_in_seconds = 10.0
    # solver.parameters.num_search_workers = 4
    logger.warning(
        f"Set max solve time to be: {solver.parameters.max_time_in_seconds} [s]"
    )
    status = solver.Solve(model, solution_cb)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        logger.info(f"Solve status: {solver.StatusName(status)}")
        logger.info(f"Total timeslots to schedule: {len(data['timeslots'])}")
        logger.debug(f"Optimal difference (lower is better): {solver.ObjectiveValue()}")
        for operating_room_idx in data["rooms"]:
            operating_room = rooms[operating_room_idx]
            total_duration = 0
            for timeslot_idx in data["timeslots"]:
                timeslot = timeslots[timeslot_idx]
                if solver.Value(x[timeslot_idx, operating_room_idx]) > 0:
                    operating_room.timeslots_to_schedule.append(timeslot)
                    total_duration += timeslot.duration

            logger.debug(
                f"Timeslots in {operating_room}: {operating_room.timeslots_to_schedule}"
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


def restructure_day_optimization_data(room: OperatingRoom, work_day_in_minutes=480):
    data = dict()
    data["timeslots"] = list(range(len(room.timeslots_to_schedule)))
    data["timeslot_durations"] = [
        timeslot.duration for timeslot in room.timeslots_to_schedule
    ]
    max_days = 1 + (sum(data["timeslot_durations"]) // work_day_in_minutes)
    data["days"] = list(range(max_days + 1))
    data["daily_limit"] = work_day_in_minutes
    return data


def distribute_timeslots_to_days(rooms: List[OperatingRoom]):
    """
    For each room, build a model that will assign operations to days such that:
        1. The total daily surgery duration will be lower than the daily operating hours
        2. (Speculation) each day has at least two kinds of surgery (short and medium, for ex.)
    """
    for room in rooms:
        data = restructure_day_optimization_data(room)
        model = cp_model.CpModel()

        # Variables ---------------------------------------------
        # x[i, j] = 1 if timeslot i is assigned to **day** j.
        x = {}
        for i in data["timeslots"]:
            for j in data["days"]:
                x[(i, j)] = model.NewIntVar(0, 1, f"x_{i}_{j}")

        # y[j] = 1 if day `j` is used.
        y = {}
        for j in data["days"]:
            y[j] = model.NewIntVar(0, 1, f"y_{j}")
        # End Variables -----------------------------------------

        # Constraints -------------------------------------------
        # Each timeslot must be scheduled in one day only.
        for timeslot in data["timeslots"]:
            model.Add(sum(x[timeslot, day] for day in data["days"]) == 1)

        # The daily duration can't exceed the maximum (work day limit)
        for day in data["days"]:
            model.Add(
                sum(
                    x[timeslot, day] * data["timeslot_durations"][timeslot]
                    for timeslot in data["timeslots"]
                )
                <= data["daily_limit"] * y[day]
            )
        # End Constraints ---------------------------------------

        # Optimization ------------------------------------------
        def days_used():
            return [y[day] for day in data["days"]]

        model.Minimize(sum(days_used()))
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL:
            logger.debug(f"[Optimization] For Room: {room}")
            timeslots = room.timeslots_to_schedule
            for day in data["days"]:
                daily_timeslots = list()
                if solver.Value(y[day]):
                    out_str = f"Day: {day} | "
                    for timeslot_idx in data["timeslots"]:
                        timeslot = timeslots[timeslot_idx]
                        if solver.Value(x[timeslot_idx, day]) > 0:
                            out_str += f" {timeslot}"
                            daily_timeslots.append(timeslot)
                    logger.debug(out_str)
                if len(daily_timeslots):
                    room.timeslots_by_day.append(daily_timeslots)
        else:
            logger.warning(f"[Optimization] Failed to solve, status: {status}")


def perform_preliminary_scheduling(
    timeslot_list: List[Timeslot], operating_rooms: List[OperatingRoom]
):
    # if len(timeslot_list) <= len(operating_rooms):
        # We have too few surgeries to schedule, or too many rooms as options
    max_rooms = min(len(timeslot_list) // 4, len(operating_rooms))
    operating_rooms = operating_rooms[:max_rooms]
    logger.debug(f"Actually using {max_rooms} rooms")
    distribute_timeslots_to_operating_rooms(timeslot_list, operating_rooms)
    distribute_timeslots_to_days(operating_rooms)
