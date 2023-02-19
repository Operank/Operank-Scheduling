from typing import List

def intersection_size(l1: List[str], l2: List[str]):
    longest_list, shortest_list = (l1, l2) if len(l1) > len(l2) else (l2, l1)
    same_elements = 0
    for element in longest_list:
        if element in shortest_list:
            same_elements += 1
    return same_elements

