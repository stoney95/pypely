from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional, Tuple, TypeVar
from pypely.memory.wrappers import MemoryEntry
import pytest

from pypely import pipeline, merge, fork, identity, to
from pypely.memory import memorizable
from pypely.core.errors import (
    PipelineStepError, 
    OutputInputDoNotMatchError, 
    ParameterAnnotationsMissingError, 
    ReturnTypeAnnotationMissingError,
    InvalidParameterAnnotationError
)

from collections import namedtuple

T = TypeVar("T")

def add(x: float, y: float) -> float:
    return x + y


@memorizable
def memory_add(x: float, y: float) -> float:
    return x + y


def mul(x: float, y: float) -> float:
    return x * y


def add_integers(x: int, y: int) -> int:
    return x + y


def untyped_add(x, y):
    return x + y


def partially_typed_add(x: int, y) -> int:
    return x + y


def add_without_return_type(x: int, y: int):
    return x + y


def to_list(val: T) -> List[T]:
    return [val]


def length(l: Iterable[T]) -> int:
    return len(list(l))


def multiply_by(x: float) -> Callable[[float], float]:
    def _multiply_by(val: float) -> float:
        return val * x

    return _multiply_by


def int_to_str(val: int) -> str:
    return str(val)


def add_keep_x(x: int, y: int) -> tuple[int, int]:
        return x, x + y


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
    with pytest.raises(ParameterAnnotationsMissingError):
        pipeline(untyped_add, to_list, length)

    with pytest.raises(ParameterAnnotationsMissingError):
        pipeline(partially_typed_add, to_list, length)

    with pytest.raises(ReturnTypeAnnotationMissingError):
        pipeline(add_without_return_type, to_list, length)


def test_pipeline_fails_if_function_types_dont_match():
    """I test that a pipeline fails if the types of two consecutive functions don't match."""
    with pytest.raises(OutputInputDoNotMatchError):
        pipeline(add, to_list, length, add)

    with pytest.raises(OutputInputDoNotMatchError):
        pipeline(add, multiply_by(0.5), int_to_str)


def test_pipeline_works_with_fork_merge():
    """I test that a pipeline works when using `fork` and `merge`.

    This is also important from the perspective of type checking.
    """
    # Prepare
    to_test = pipeline(
        add,
        fork(
            multiply_by(1.2),
            multiply_by(0.4)
        ),
        merge(add),
        to_list
    )

    # Act
    result = to_test(1, 1)

    # Compare
    assert result == [3.2]


def test_pipeline_with_multiple_or_no_output_steps():
    # Prepare
    def no_output(x: float) -> None:
        print(x)

    def no_input() -> float:
        return 3.4

    to_test = pipeline(
        add_keep_x,
        add,
        no_output,
        no_input
    )

    # Act
    result = to_test(1,1)

    # Compare
    assert result == 3.4


def test_pipeline_with_optional_input_steps():
    # Prepare
    def optional_add(x: int, y: Optional[int]=None) -> int:
        if y is None:
            return x
        return x + y

    to_test = pipeline(
        add_keep_x,
        optional_add,
        to_list,
        length,
        optional_add
    )

    # Act
    result = to_test(1,2)

    # Compare
    assert result == 1


def test_pipeline_fails_safely_with_non_matching_multiple_output_function():
    # Prepare
    def create_triple(val: float) -> Tuple[float, float, float]:
        return (val, val, val)

    with pytest.raises(OutputInputDoNotMatchError):
        pipeline(
            add,
            create_triple,
            add
        )



def test_pipeline_works_with_memory():
    """I test that a pipeline works when the memory is used.

    This is als important from the perspective of type checking.
    """
    @memorizable
    def sum_values(val1: float, val2: float, val3: float) -> float:
        return val1 + val2 + val3

    first_sum = MemoryEntry()

    # Prepare
    to_test = pipeline(
        memory_add >> first_sum,
        to_list,
        length,
        first_sum >> memory_add >> "second_sum",
        to_list,
        length,
        memory_add << "second_sum",
        sum_values << first_sum << "second_sum",
        first_sum >> sum_values << "second_sum",
        first_sum >> ("second_sum" >> sum_values)
    )

    # Act
    result = to_test(1,2)

    # Compare
    assert result == 26

@pytest.mark.skip("Asterisk functions are not yet accepted")
def test_pipeline_works_with_asterisk_function():
    # Prepare
    def sum_values(*args: float) -> float:
        return sum(args)

    def create_tuple_of_ones(length: int) -> tuple[int, ...]:
        return (1,) * length

    to_test = pipeline(
        create_tuple_of_ones,
        sum_values
    )

    # Act
    result = to_test(5)

    # Compare
    assert result == 5


def test_pipeline_fails_for_asterisk_function_with_invalid_parameter_definition():
    # Prepare
    def sum_values(*args: float) -> float:
        return sum(args)

    def create_tuple_of_ones(length: int) -> tuple[int, ...]:
        return (1,) * length
    
    with pytest.raises(InvalidParameterAnnotationError):
        pipeline(
            create_tuple_of_ones,
            sum_values
        )


def test_pipeline_fails_for_keyword_only_function_with_invalid_parameter_definition():
    # Prepare
    def sum_values(first: float, *, second: float) -> float:
        return first + second

    def create_tuple_of_ones(length: int) -> tuple[int, ...]:
        return (1,) * length
    
    with pytest.raises(InvalidParameterAnnotationError):
        pipeline(
            create_tuple_of_ones,
            sum_values
        )


def test_pipeline_fails_for_double_asterisk_function_with_invalid_parameter_definition():
    # Prepare
    def sum_values(**kwargs: float) -> float:
        return sum(kwargs.values())

    def create_tuple_of_ones(length: int) -> tuple[int, ...]:
        return (1,) * length
    
    with pytest.raises(InvalidParameterAnnotationError):
        pipeline(
            create_tuple_of_ones,
            sum_values
        )


def test_pipeline_fails_safely_with_failing_function():
    """I test that the right error is raised when a function inside a pipeline fails."""
    # Prepare
    def i_fail(val: float) -> float:
        raise RuntimeError("I have to fail")

    to_test = pipeline(add, i_fail)

    # Act
    with pytest.raises(PipelineStepError):
        to_test(1,2)

    with pytest.raises(PipelineStepError):
        to_test(1,2,3)


def test_pipeline_can_be_used_as_input_to_other_pipeline():
    """I test that a pipeline could be used as an input to another pipeline"""
    # Prepare
    inner_pipeline = pipeline(
        add, multiply_by(3)
    )

    to_test = pipeline(
        add,
        fork(
            multiply_by(2),
            multiply_by(4)
        ),
        merge(inner_pipeline),
        to_list
    )

    # Act
    result = to_test(1,2)

    # Compare
    assert result == [54]


def test_pipeline_with_to():
    """I test that `to` can be used in a `pipeline`"""
    # Prepare
    @dataclass
    class TestObject():
        val1: float
        val2: float

    to_test = pipeline(
        add,
        fork(
            multiply_by(1.5),
            multiply_by(2.5)
        ),
        to(TestObject)
    )

    # Act
    result = to_test(1,1)

    # Compare
    assert result == TestObject(3.0, 5.0)


def test_pipeline_with_to_using_fields():
    @dataclass
    class TestObject():
        val1: float
        val2: float

    def process_object(obj: TestObject) -> float:
        return obj.val1 - obj.val2

    to_test = pipeline(
        add,
        fork(
            multiply_by(1.5),
            multiply_by(2.5)
        ),
        to(TestObject, "val2", "val1"),
        process_object
    )

    # Act
    result = to_test(1,1)

    # Compare
    assert result == 2.0


def test_pipeline_with_identity():
    # Prepare
    to_test = pipeline(
        add,
        fork(
            multiply_by(1.5),
            multiply_by(0.5)
        ),
        identity,
        merge(add)
    )

    # Act
    result = to_test(1, 1)

    # Compare
    assert result == 4.0