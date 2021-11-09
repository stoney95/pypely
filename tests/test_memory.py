from pypely.memory import add_to_memory, use_memory, with_memory_attribute
from pypely import pipeline, fork, merge

import pytest

def test_multiple_layers_access_fails(add, mul, sub):
    inner_pipe = pipeline(
        with_memory_attribute("first_sum", mul),
        with_memory_attribute("first_product", add)
    )

    to_test = pipeline(
        fork(
            add_to_memory("first_sum", add), 
            add_to_memory("first_product", mul), 
        ),
        merge(sub),
        inner_pipe
    )

    with pytest.raises(AttributeError):
        to_test(1,2)


def test_memory_access(add, mul, sub):
    test_function = pipeline(
        fork(
            add_to_memory("first_sum", add), 
            add_to_memory("first_product", mul), 
        ),
        merge(sub),
        with_memory_attribute("first_sum", mul),
        with_memory_attribute("first_product", add)
    )

    to_test = test_function(1,2)

    assert to_test == 5


