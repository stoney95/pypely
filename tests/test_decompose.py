from typing import Callable

import pytest

from pypely import pipeline, merge, fork
from pypely.components import decompose, Operation, Pipeline, Fork, Merge, Memorizable
from pypely.memory import memorizable
from pypely.memory.wrappers import _add_to_memory

@memorizable(allow_ingest=True)
def add(x: float, y: float) -> float:
    return x + y

def multiply_by(x: float) -> Callable[[float], float]:
    def _multiply_by(val: float) -> float:
        return val * x

    return _multiply_by

@memorizable
def devide_by(x: float) -> Callable[[float], float]:
    def _devide_by(val: float) -> float:
        return val / x
    return _devide_by

@pytest.mark.skip("Decompose is not working with the new implementation as it relies on outdated data structure `DebugMemory`")
def test_decompose():
    test = pipeline(
        add >> "sum1",
        fork(
            multiply_by(5),
            multiply_by(10)
        ),
        merge(add),
        add << "sum1",
        devide_by(5)
    )

    components = decompose(test)

    to_test = Pipeline(steps=[
        # _add_to_memory is used to simulate the usage of 'add >> "sum1"'
        # add.func is used because that happens inside pypely.memory.wrappers.Memorizable when 'add >> "sum1"' is called
        Memorizable(func=Operation(func=_add_to_memory(add.func, "sum1"))), 
        Fork(branches=[
            Operation(func=multiply_by(5)),
            Operation(func=multiply_by(10)),
        ]),
        Merge(func=add),
        Memorizable(func=Operation(func=add)),
        Operation(func=devide_by(5))
    ])

    assert to_test == components
