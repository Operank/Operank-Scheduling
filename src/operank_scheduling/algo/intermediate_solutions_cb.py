import time
from typing import Dict, List

from loguru import logger
from ..models.operank_models import OperatingRoom, Timeslot
from ortools.sat.python import cp_model


class SurgeryToRoomSolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(
        self, data: Dict, timeslots: List[Timeslot], rooms: List[OperatingRoom], x
    ):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.data = data
        self.timeslots = timeslots
        self.rooms = rooms
        self.solution_count = 0
        self.start_time = time.time()
        self.x = x

    def find_total_lengths(self):
        operating_room_timeslot_lengths = []
        for operating_room_idx in self.data["rooms"]:
            total_duration = 0
            for timeslot_idx in self.data["timeslots"]:
                timeslot = self.timeslots[timeslot_idx]
                if self.Value(self.x[timeslot_idx, operating_room_idx]) > 0:
                    total_duration += timeslot.duration
            operating_room_timeslot_lengths.append(total_duration)
        return operating_room_timeslot_lengths

    def on_solution_callback(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.solution_count += 1
        operating_room_timeslot_lengths = self.find_total_lengths()

        logger.debug(
            f"[S{self.solution_count}] @ {elapsed_time:.2f}s =============="
            f"\nDurations: {operating_room_timeslot_lengths}"
        )
