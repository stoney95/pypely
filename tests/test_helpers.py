from pypely.helpers import reduce_by, flatten


def test_reduce_by(add):
    partial_add = reduce_by(add)

    to_test = partial_add(1,2,3,4,5)
    assert to_test == (3, (3,4,5))


def test_flatten():
    nested_list = [1, 2, [3, [4, 5], 6], 7, [8, [9]]]
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    to_test = flatten(nested_list)

    assert to_test == expected