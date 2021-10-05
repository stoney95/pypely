from pypely.helpers import *


def test_reduce_by(add):
    partial_add = reduce_by(add)

    to_test = partial_add(1,2,3,4,5)
    assert to_test == (3, (3,4,5))


def test_flatten():
    nested_list = [1, 2, [3, [4, 5], 6], 7, [8, [9]]]
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    to_test = flatten(nested_list)

    assert to_test == expected


def test_side_effect():
    def __print(*x):
        message = ' '.join(x)
        print(f"Hi! 🤗 I'm a super nice side effect. Even if I try the input says: {message}")
        return message

    test_function = side_effect(__print)
    to_test = test_function("Can't", "touch", "me")

    assert to_test == ("Can't", "touch", "me")


def test_head():
    _list = [1,2,3,4,5]
    to_test = head(_list)

    assert to_test == 1


def test_rest():
    _list = [1,2,3,4,5]
    to_test = rest(_list)

    assert to_test == [2,3,4,5]