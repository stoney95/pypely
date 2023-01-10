from typing import Any, Callable, Iterable, List, TypeVar
import pytest

from pypely import pipeline, merge, fork, identity, to
from pypely.helpers import head, rest, reduce_by
from pypely._types import PypelyTuple
from pypely.core.errors import MergeError, PipelineForwardError, PipelineCallError, PipelineStepError

from collections import namedtuple

T = TypeVar("T")

def add(x: float, y: float) -> float:
    return x + y


def mul(x: float, y: float) -> float:
    return x * y


def add_integers(x: int, y: int) -> int:
    return x + y


def untyped_add(x, y):
    return x + y


def partially_typed_add(x: int, y) -> int:
    return x + y


def to_list(val: T) -> List[T]:
    return [val]


def length(l: Iterable[T]) -> int:
    return len(list(l))


def multiply_by(x: float) -> Callable[[float], float]:
    def _multiply_by(val: float) -> float:
        return val * x

    return _multiply_by



def test_pipeline_works_in_general():
    """I test that a simple pipeline works.

    This includes that the functions of the pipeline are typed correctly.
    """
    # Prepare
    to_test = pipeline(
        add,
        multiply_by(5),
        multiply_by(2)
    )

    input = (1,2)
    expected_result = 30

    # Act
    result = to_test(*input)

    # Compare
    assert result == expected_result


def test_pipeline_works_with_subtype_functions():
    """I test that the type checks also work with subtypes.

    This will use functions which outputs are typed as concrete types, e.g. List, Dict, etc.
    The inputs of the following function are typed with generic types, e.g. Iterable.
    """
    # Prepare
    to_test = pipeline(
        add_integers,
        to_list,
        length,
        multiply_by(5),
        multiply_by(2),
    )

    input = (1,2)
    expected_result = 10

    # Act
    result = to_test(*input)

    # Compare
    assert result == expected_result


def test_pipeline_fails_with_untyped_functions():
    """I test that a pipeline fails if an untyped function is used."""


def test_pipeline_fails_if_function_types_dont_match():
    """I test that a pipeline fails if the types of two consecutive functions don't match."""


def test_pipeline_works_with_fork_merge():
    """I test that a pipeline works when using `fork` and `merge`.

    This is also important from the perspective of type checking.
    """


def test_pipeline_works_with_memory():
    """I test that a pipeline works when the memory is used.

    This is als important from the perspective of type checking.
    """


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


def test_fail_pipeline_step(add):
    def raise_error(x):
        return x / 0

    add_to_5 = lambda x: x+5
    pipe = pipeline(
        add,
        add_to_5,
        raise_error
    )

    with pytest.raises(PipelineStepError):
        pipe(1, 2)


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


def test_fail_merge():
    single = merge(
        lambda x, y: x*y
    )

    with pytest.raises(MergeError):
        single(PypelyTuple(1, PypelyTuple(2,3)))


def test_identity():
    to_test = identity(1, 2)

    assert to_test == (1, 2)
