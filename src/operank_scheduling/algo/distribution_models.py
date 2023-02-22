from ortools.sat.python import cp_model
import numpy as np
from typing import Dict
from math import factorial

MAX_VAL_LIM = 10000

def create_data_dict() -> Dict:
    """Create the data for the example."""
    data = dict()
    operating_rooms = 3
    surgery_durations = [120, 60, 60, 120, 180, 60]
    data['avg_duration'] = int(np.mean(surgery_durations) * len(surgery_durations))
    data['surgery_durations'] = surgery_durations
    data['surgeries'] = list(range(len(surgery_durations)))
    data['rooms'] = list(range(operating_rooms))
    data['min_total_duration'] = min(surgery_durations) * len(surgery_durations) // operating_rooms
    data['max_total_duration'] = max(surgery_durations) * len(surgery_durations) // operating_rooms
    return data

def lazy_permute(in_lst: list) -> list:
    out_lst = list()
    for i in range(len(in_lst)):
        for j in range(i+1, len(in_lst)):
            out_lst.append( (in_lst[i], in_lst[j]) )
    return out_lst


def main():
    data = create_data_dict()
    # Create the mip solver with the SCIP backend.
    model = cp_model.CpModel()

    # Variables ---------------------------------------------
    # x[i, j] = 1 if surgery i is assigned to room j.
    x = {}
    for i in data['surgeries']:
        for j in data['rooms']:
            x[(i, j)] = model.NewIntVar(0, 1, f'x_{i}_{j}')

    absolute_length_differences = [model.NewIntVar(0, MAX_VAL_LIM, f"diff_{i}") for i in range (factorial(len(data['rooms'])))]

    # Constraints -------------------------------------------
    # Each surgery must be in exactly one room. 
    for surgery in data['surgeries']:
        model.AddExactlyOne(x[surgery, j] for j in data['rooms'])
    
    # Each room should have at least one surgery.
    # for j in data['rooms']:
    #     model.Add(sum(x[i, j] for i in data['surgeries']) >= 1)

    # # The total duration in each room should be smaller and up to the average duration
    # for j in data['rooms']:
    #     model.Add(sum(x[(i, j)] * data['surgery_durations'][i] for i in data['surgeries']) <= data['avg_duration'])
    
    def total_room_duration(room):
        return sum([x[(surgery, room)] * data['surgery_durations'][surgery] for surgery in data['surgeries']])

    for j in data['rooms']:
        # model.Add(total_room_duration(j) >= data['min_total_duration'])  # Possibly not required
        model.Add(total_room_duration(j) <= data['max_total_duration'])

    def total_room_duration_differences():
        total_room_durations = [total_room_duration(room) for room in data['rooms']]
        all_perms = lazy_permute(total_room_durations)
        for idx, permutation in enumerate(all_perms):
            temp = model.NewIntVar(-MAX_VAL_LIM, MAX_VAL_LIM, f"temp_{idx}")  # temporary variable, as a workaround for abs val
            model.Add( temp == (permutation[0] - permutation[1]))
            model.AddAbsEquality(absolute_length_differences[idx], temp)


    total_room_duration_differences()

    model.Minimize(sum(absolute_length_differences))
    solver = cp_model.CpSolver()
    # solver.parameters.linearization_level = 0

    # solver.parameters.enumerate_all_solutions = True
    status = solver.Solve(model)
    print('Solve status: %s' % solver.StatusName(status))


    if status == cp_model.OPTIMAL:
        print(f"Total surgeries to schedule: {len(data['surgeries'])}")
        print(f"Optimal difference (lower is better): {solver.ObjectiveValue()}")
        for j in data['rooms']:
            assigned_surgeries = []
            total_duration = 0
            for i in data['surgeries']:
                if solver.Value(x[i, j]) > 0:
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
 