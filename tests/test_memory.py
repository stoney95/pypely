from pypely import pipeline, fork, merge
from pypely.memory import memorizable
from pypely.memory.errors import *

import pytest

def test_multiple_layers_access_fails(add, mul, sub):
    _mul = memorizable(mul)
    _add = memorizable(add)

    inner_pipe = pipeline(
        _mul << "first_sum",
        _add << "first_product"
    )

    to_test = pipeline(
        fork(
            _add >> "first_sum",
            _mul >> "first_product", 
        ),
        merge(sub),
        inner_pipe
    )

    with pytest.raises(MemoryAttributeNotFoundError):
        to_test(1,2)


def test_memory_access(add, mul, sub):
    _mul = memorizable(mul)
    _add = memorizable(add)

    test_function = pipeline(
        fork(
            _add >> "first_sum",
            _mul >> "first_product",
        ),
        merge(sub),
        _mul << "first_sum",
        _add << "first_product"
    )

    to_test = test_function(1,2)

    assert to_test == 5


def test_memorizable(add, mul, sub):
    @memorizable
    def sum_values(*args):
        return sum(args)

    _add = memorizable(add)
    _mul = memorizable(mul)

    test_function = pipeline(
        fork(
            _add >> "first_sum", 
            _mul >> "first_product", 
        ),
        merge(sub),
        _mul << "first_sum",
        _add << "first_product",
        "first_product" >> sum_values << "first_sum" << "first_product" << "first_sum"
    )

    to_test = test_function(1,2)

    assert to_test == 15


def test_no_double_attr_assignment(add):
    _add = memorizable(add)

    to_test = fork(
        _add >> "first_sum",
        _add >> "first_sum"
    )

    with pytest.raises(MemoryAttributeExistsError):
        to_test(1,2)


def test_memorizable_as_normal_func(add):
    _add = memorizable(add)

    to_test = _add(1,2)
    assert to_test == 3


def test_memory_access_outside_pipeline(add):
    _add = memorizable(add)

    to_test = _add >> "test"
    to_test(1,2)

    try_access = _add << "test"
    assert try_access(1) == 4


def test_unallowed_memory_ingest(add):
    _add = memorizable(add, allow_ingest=False)

    with pytest.raises(MemoryIngestNotAllowedError):
        pipeline(
            _add >> "result",
            _add << "result"
        )


def test_memory_decorator_allow_ingest_works():
    @memorizable(allow_ingest=True)
    def add(x, y):
        return x + y

    @memorizable(allow_ingest=False)
    def subtract(x, y):
        return x - y

    test = pipeline(
        subtract >> "result",
        add << "result"
    )

    assert test(2,1) == 2


def test_memory_decorator_allow_ingest_fails():
    @memorizable(allow_ingest=True)
    def add(x, y):
        return x + y

    @memorizable(allow_ingest=False)
    def subtract(x, y):
        return x - y

    with pytest.raises(MemoryIngestNotAllowedError):
        pipeline(
            add >> "result",
            subtract << "result"
        )


def test_memory_consumption_and_writing():
    @memorizable(allow_ingest=True)
    def add(x, y):
        return x + y

    test = pipeline(
        add >> "sum1",
        add << "sum1" >> "sum2",
        add << "sum2"
    )

    assert test(1,1) == 8