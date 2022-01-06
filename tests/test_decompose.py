import pytest

from pypely import pipeline, merge, fork
from pypely.components import decompose, Operation, Pipeline, Fork, Merge, Memorizable
from pypely.memory import memorizable
from pypely.memory.wrappers import _add_to_memory

@memorizable(allow_ingest=True)
def add(x, y):
    return x + y

def multiply_by(x):
    return lambda y: x * y

def devide_by(x):
    return lambda y: y / x

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
