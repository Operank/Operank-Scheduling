from src.operank_scheduling.algo.algo_helpers import intersection_size


def test_intersection_size():
    assert intersection_size([1], [1, 2]) == 1
    assert intersection_size([1, 2], [1, 2]) == 2
    assert intersection_size([3], [1, 2]) == 0
    assert intersection_size([1, 2, 3], [1, 2]) == 2
