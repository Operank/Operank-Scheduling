from src.operank_scheduling.algo.algo_helpers import intersection_size, lazy_permute


def test_intersection_size():
    assert intersection_size([1], [1, 2]) == 1
    assert intersection_size([1, 2], [1, 2]) == 2
    assert intersection_size([3], [1, 2]) == 0
    assert intersection_size([1, 2, 3], [1, 2]) == 2


def test_lazy_permute():
    assert lazy_permute([1, 2, 3, 5]) == [(1, 2), (1, 3), (1, 5), (2, 3), (2, 5), (3, 5)]
    assert lazy_permute([]) == []
    assert lazy_permute([1]) == []
