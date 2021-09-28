import pytest
from pypely import flatten


def test_flatten():
    nested_list = [1, 2, [3, [4, 5], 6], 7, [8, [9]]]
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    to_test = flatten(nested_list)

    assert to_test == expected