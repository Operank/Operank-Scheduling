from ortools.linear_solver import pywraplp
import numpy as np
from typing import Dict
import itertools

def create_data_dict() -> Dict:
    """Create the data for the example."""
    data = dict()
    operating_rooms = 2
    surgery_durations = [120, 60, 12, 120]
    data['avg_duration'] = max(surgery_durations) * len(surgery_durations) / operating_rooms
    data['surgery_durations'] = surgery_durations
    data['surgeries'] = list(range(len(surgery_durations)))
    data['rooms'] = list(range(operating_rooms))
    return data



def main():
    data = create_data_dict()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    if not solver:
        return

    # Variables ---------------------------------------------
    # x[i, j] = 1 if surgery i is assigned to room j.
    x = {}
    for i in data['surgeries']:
        for j in data['rooms']:
            x[(i, j)] = solver.IntVar(0, 1, f'x_{i}_{j}')


    # Constants ---------------------------------------------
    # Operations that are already assigned (1:1) are set here
    x[(3, 0)] = 1  # TODO

    # Constraints -------------------------------------------
    # Each surgery must be in exactly one room.
    for i in data['surgeries']:
        solver.Add(sum(x[i, j] for j in data['rooms']) == 1)

    # The total duration in each room should be up to the average 
    for j in data['rooms']:
        solver.Add(sum(x[(i, j)] * data['surgery_durations'][i] for i in data['surgeries']) <= data['avg_duration'])
    


    def total_room_duration(room):
        # return sum([x[(surgery, room)] * data['surgery_durations'][surgery] for surgery in data['surgeries']]) - data['avg_duration']
        return sum([x[(surgery, room)] * data['surgery_durations'][surgery] for surgery in data['surgeries']])

    def total_room_duration_differences():
        total_room_durations = [total_room_duration(room) for room in data['rooms']]
        all_permutations = list(itertools.permutations(total_room_durations, r=2))
        return [i-j for i,j in all_permutations]

    
    solver.Minimize(solver.Sum(total_room_duration_differences()))
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.INFEASIBLE:
        print(f"Total surgeries to schedule: {len(data['surgeries'])}")
        for j in data['rooms']:
            assigned_surgeries = []
            total_duration = 0
            for i in data['surgeries']:
                try:
                    if x[i, j].solution_value() > 0:
                        assigned_surgeries.append(i)
                        total_duration += data['surgery_durations'][i]
                except Exception as e:
                    if x[i, j] == 1:
                        assigned_surgeries.append(i)
                        total_duration += data['surgery_durations'][i]
            if assigned_surgeries:
                print(f'Surgeries in OR{j}:', assigned_surgeries)
                print('Daily Surgery Length:', total_duration)
                print()
        print()
        print('Time = ', solver.WallTime(), ' milliseconds')
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    main()
 