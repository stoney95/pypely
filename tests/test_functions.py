import pytest
from pypely import pipeline, merge, fork, identity, reduce_by
from pypely.functions import flatten

add = lambda x, y: x + y
mul = lambda x, y: x * y
sub = lambda x, y: x - y
head = lambda x: x[0]
rest = lambda x: x[1:]


def test_pypely():
    quadratic_pipe = pipeline(
        head,
        fork(identity, identity),
        merge(mul)
    )

    pipe = pipeline(
        reduce_by(add),
        fork(quadratic_pipe, rest),
        merge(sub)
    )

    to_test = pipe(3, 4, 7)
    assert to_test == 42


def test_pipeline():
    add_to_5 = lambda x: x+5
    add_to_4 = lambda x: x+4
    add_to_3 = lambda x: x+3

    pipe = pipeline(
        add_to_3, 
        add_to_4,
        add_to_5
    )

    to_test = pipe(3)
    assert to_test == 15


def test_reduce_by():
    partial_add = reduce_by(add)

    to_test = partial_add(1,2,3,4,5)
    assert to_test == (3, (3,4,5))


def test_fork():
    multiple = fork(
        add, mul, sub
    )

    to_test = multiple(2, 1)
    assert to_test == [3, 2, 1]


def test_merge():
    single = merge(
        lambda x, y, z: x*y+z
    )

    to_test = single([1,2,3])
    assert to_test == 5


def test_flatten():
    nested_list = [1, 2, [3, [4, 5], 6], 7, [8, [9]]]
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    to_test = flatten(nested_list)

    assert to_test == expected