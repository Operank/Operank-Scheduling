from typing import List


def intersection_size(l1: List[str], l2: List[str]):
    longest_list, shortest_list = (l1, l2) if len(l1) > len(l2) else (l2, l1)
    num_same_elements = 0
    for element in longest_list:
        if element in shortest_list:
            num_same_elements += 1
    return num_same_elements


def lazy_permute(in_lst: List) -> List:
    if len(in_lst) < 2:
        return list()
    permutations = list()
    for i in range(len(in_lst)):
        for j in range(i + 1, len(in_lst)):
            permutations.append((in_lst[i], in_lst[j]))
    return permutations
