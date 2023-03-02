import time
from loguru import logger
from typing import Dict, List
import numpy as np

from models.operank_models import OperatingRoom, Surgery
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

    def find_total_lengths(self):
        operating_room_surgery_lengths = []
        for operating_room_idx in self.data["rooms"]:
            total_duration = 0
            for surgery_idx in self.data["surgeries"]:
                surgery = self.surgeries[surgery_idx]
                if self.Value(self.x[surgery_idx, operating_room_idx]) > 0:
                    total_duration += surgery.duration
            operating_room_surgery_lengths.append(total_duration)
        return operating_room_surgery_lengths

    def on_solution_callback(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.solution_count += 1
        operating_room_surgery_lengths = self.find_total_lengths()

        avg = np.mean(operating_room_surgery_lengths)
        logger.debug(
            f"[S{self.solution_count}] @ {elapsed_time:.2f}s =============="
            f"\nDurations: {operating_room_surgery_lengths}"
            f"\nMean-Deltas: {[v - avg for v in operating_room_surgery_lengths]}"
        )
