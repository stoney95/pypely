import pytest

from pypely import pipeline, merge, fork, identity, to
from pypely.helpers import head, rest, reduce_by
from pypely._types import PypelyTuple
from pypely.core.errors import PipelineForwardError, PipelineCallError

from collections import namedtuple


def test_pypely(add, mul, sub):
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


def test_pipeline_single_function(add):
    pipe = pipeline(
        add
    )

    to_test = pipe(1,2)
    assert to_test == 3


def test_fail_pipeline_forward(add):
    add_to_5 = lambda x: x+5

    pipe = pipeline(
        add_to_5,
        add
    )

    with pytest.raises(PipelineForwardError):
        pipe(1)


def test_fail_pipeline_call(add):
    add_to_5 = lambda x: x+5
    pipe = pipeline(
        add, 
        add_to_5
    )

    to_test = pipe(1,2)
    assert to_test == 8

    with pytest.raises(PipelineCallError):
        pipe(1)


def test_fork(add, mul, sub):
    multiple = fork(
        add, mul, sub
    )

    to_test = multiple(2, 1)
    assert to_test == PypelyTuple(3, 2, 1)


def test_to_with_field_names(add, mul, sub):
    Triple = namedtuple('Triple', ['x', 'y', 'z'])

    to_triple = pipeline(
        fork(
            sub, mul, add
        ),
        to(Triple, "x", "y", "z")
    )

    to_test = to_triple(2,1)
    expected = Triple(1, 2, 3)

    assert to_test == expected


def test_to_no_field_names(add, mul, sub):
    Triple = namedtuple('Triple', ['x', 'y', 'z'])

    to_triple = pipeline(
        fork(
            add, mul, sub
        ),
        to(Triple)
    )

    to_test = to_triple(2,1)
    expected = Triple(3, 2, 1)

    assert to_test == expected


def test_merge():
    single = merge(
        lambda x, y, z: x*y+z
    )

    to_test = single(PypelyTuple(1, PypelyTuple(2,3)))
    assert to_test == 5


def test_identity():
    to_test = identity(1, 2)

    assert to_test == (1, 2)
