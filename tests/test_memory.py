import pytest

from pypely import fork, merge, pipeline
from pypely._types import PypelyTuple
from pypely.memory import MemoryEntry, memorizable
from pypely.memory.errors import MemoryAttributeExistsError, MemoryAttributeNotFoundError, MemoryIngestNotAllowedError


def mul(x: float, y: float) -> float:
    return x * y


def add(x: float, y: float) -> float:
    return x + y


def sub(x: float, y: float) -> float:
    return x - y


def test_multiple_layers_access_fails():
    _mul = memorizable(mul)
    _add = memorizable(add)

    with pytest.raises(MemoryAttributeNotFoundError):
        inner_pipe = pipeline(_mul << "first_sum", _add << "first_product")

        to_test = pipeline(
            fork(
                _add >> "first_sum",
                _mul >> "first_product",
            ),
            merge(sub),
            inner_pipe,
        )

        to_test(1, 2)


def test_memory_access():
    _mul = memorizable(mul)
    _add = memorizable(add)

    test_function = pipeline(
        fork(
            _add >> "first_sum",
            _mul >> "first_product",
        ),
        merge(sub),
        _mul << "first_sum",
        _add << "first_product",
    )

    to_test = test_function(1, 2)

    assert to_test == 5


def test_memorizable():
    @memorizable
    def sum_4_values(val1: float, val2: float, val3: float, val4: float) -> float:
        return val1 + val2 + val3 + val4

    _add = memorizable(add)
    _mul = memorizable(mul)

    first_sum = MemoryEntry()
    first_product = MemoryEntry()

    test_function = pipeline(
        fork(
            _add >> first_sum,
            _mul >> first_product,
        ),
        merge(sub),
        _mul << first_sum,
        _add << first_product,
        first_product >> sum_4_values << first_sum << first_product,
    )

    to_test = test_function(1, 2)

    assert to_test == 12


def test_memorizable_pipeline():
    _add = memorizable(add)

    def add_2(x: float) -> float:
        return x + 2

    inner = pipeline(add, add_2)

    test = pipeline(_add >> "test", inner << "test")

    assert test(1, 1) == 6


def test_memorizable_fork_merge():
    _add = memorizable(add)

    def add_2(x: float) -> float:
        return x + 2

    @memorizable
    def add_first(x: float, results: PypelyTuple) -> float:
        _results = list(results)
        return x + _results[0]

    forked_add = fork(add_2, add_2) >> "forked"

    to_test = pipeline(add, forked_add, merge(add) >> "merged", add_first << "forked", _add << "merged")

    assert to_test(1, 1) == 20


def test_no_double_attr_assignment():
    _add = memorizable(add)

    with pytest.raises(MemoryAttributeExistsError):
        fork(_add >> "first_sum", _add >> "first_sum")


def test_memorizable_as_normal_func():
    _add = memorizable(add)

    to_test = _add(1, 2)
    assert to_test == 3


def test_memory_access_outside_pipeline():
    _add = memorizable(add)

    test = MemoryEntry()

    to_test = _add >> test
    to_test(1, 2)

    try_access = _add << test
    assert try_access(1) == 4


def test_unallowed_memory_ingest():
    _add = memorizable(add, allow_ingest=False)

    with pytest.raises(MemoryIngestNotAllowedError):
        pipeline(_add >> "result", _add << "result")


def test_memory_decorator_allow_ingest_works():
    @memorizable(allow_ingest=True)
    def add(x: float, y: float) -> float:
        return x + y

    @memorizable(allow_ingest=False)
    def subtract(x: float, y: float) -> float:
        return x - y

    result = MemoryEntry()

    test = pipeline(subtract >> result, add << result)

    assert test(2, 1) == 2


def test_memory_decorator_allow_ingest_fails():
    @memorizable(allow_ingest=True)
    def add(x: float, y: float) -> float:
        return x + y

    @memorizable(allow_ingest=False)
    def subtract(x: float, y: float) -> float:
        return x - y

    result = MemoryEntry()

    with pytest.raises(MemoryIngestNotAllowedError):
        pipeline(add >> result, subtract << result)


def test_memory_consumption_and_writing():
    @memorizable(allow_ingest=True)
    def add(x: float, y: float) -> float:
        return x + y

    test = pipeline(add >> "sum1", add << "sum1" >> "sum2", add << "sum2")

    assert test(1, 1) == 8
