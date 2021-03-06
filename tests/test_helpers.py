from pypely.helpers import *
from pypely._types import PypelyTuple

import pytest

def test_reduce_by(add):
    partial_add = reduce_by(add)

    to_test = partial_add(1,2,3,4,5)
    assert to_test == (3,3,4,5)


def test_flatten():
    nested_tuple = PypelyTuple(1, 2, PypelyTuple(3, PypelyTuple(4, 5), 6), 7, PypelyTuple(8, PypelyTuple(9)))
    expected = PypelyTuple(1, 2, 3, 4, 5, 6, 7, 8, 9)

    to_test = flatten(nested_tuple)

    assert to_test == expected
    assert type(to_test) == PypelyTuple


def test_flatten_fail():
    nested_tuple = (1,(2,3), 4)

    with pytest.raises(ValueError):
        flatten(nested_tuple)


def test_side_effect():
    def __print(*x):
        message = ' '.join(x)
        print(f"Hi! 🤗 I'm a super nice side effect. Even if I try the input says: {message}")
        return message

    test_function = side_effect(__print)
    to_test = test_function("Can't", "touch", "me")

    assert to_test == ("Can't", "touch", "me")


def test_side_effect_single_argument():
    def __print(*x):
        message = ' '.join(x)
        print(message)
        return 5000

    test_function = side_effect(__print)
    to_test = test_function("Test")

    assert to_test == "Test"
    


def test_head():
    _list = [1,2,3,4,5]
    to_test = head(_list)

    assert to_test == 1


def test_rest():
    _list = [1,2,3,4,5]
    to_test = rest(_list)

    assert to_test == PypelyTuple(2,3,4,5)


def test_optional(add):
    optional_add = optional(add, lambda x: x > 10)

    not_added = optional_add(1, 2)
    added = optional_add(11, 3)

    assert not_added == (1,2)
    assert added == 14
