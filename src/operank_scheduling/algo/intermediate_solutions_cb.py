import time
from loguru import logger
from typing import Dict, List
import numpy as np

from models.operating_room import OperatingRoom
from models.surgery import Surgery
from ortools.sat.python import cp_model


class SurgeryToRoomSolutionCallback(cp_model.CpSolverSolutionCallback):

    def __init__(self, data: Dict,
                 surgeries: List[Surgery],
                 rooms: List[OperatingRoom],
                 x):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.data = data
        self.surgeries = surgeries
        self.rooms = rooms
        self.solution_count = 0
        self.start_time = time.time()
        self.x = x

    def on_solution_callback(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        logger.debug(f" ==== Solution {self.solution_count} time = {elapsed_time:.2f}[s] ==== ")
        self.solution_count += 1
        operating_room_surgery_lengths = []
        # Print the solution:
        for operating_room_idx in self.data["rooms"]:
            total_duration = 0
            for surgery_idx in self.data["surgeries"]:
                surgery = self.surgeries[surgery_idx]
                if self.Value(self.x[surgery_idx, operating_room_idx]) > 0:
                    total_duration += surgery.duration
            operating_room_surgery_lengths.append(total_duration)
            # logger.debug(
            #     f"Surgeries in {operating_room}: {operating_room.surgeries_to_schedule}"
            # )
        logger.debug(
            f"Durations: {operating_room_surgery_lengths}, avg: {np.mean(operating_room_surgery_lengths)}"
        )
