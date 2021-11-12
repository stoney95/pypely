from pypely.memory import add_to_memory, with_memory_attribute, memorizable
from pypely import pipeline, fork, merge

import pytest

def test_multiple_layers_access_fails(add, mul, sub):
    inner_pipe = pipeline(
        with_memory_attribute(mul, "first_sum"),
        with_memory_attribute(add, "first_product")
    )

    to_test = pipeline(
        fork(
            add_to_memory(add, "first_sum"), 
            add_to_memory(mul, "first_product"), 
        ),
        merge(sub),
        inner_pipe
    )

    with pytest.raises(AttributeError):
        to_test(1,2)


def test_memory_access(add, mul, sub):
    test_function = pipeline(
        fork(
            add_to_memory(add, "first_sum"), 
            add_to_memory(mul, "first_product"), 
        ),
        merge(sub),
        with_memory_attribute(mul, "first_sum"),
        with_memory_attribute(add, "first_product")
    )

    to_test = test_function(1,2)

    assert to_test == 5


def test_memorizable(add, mul, sub):
    @memorizable
    def sum_values(x, *args):
        return x + sum(args)

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