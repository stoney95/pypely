from typing import Callable
from inspect import getfullargspec
from ._types import PypelyTuple


def reduce_by(func: Callable) -> Callable:
    num_args = len(getfullargspec(func).args)
    return lambda *x: flatten(PypelyTuple(func(*x[:num_args]), *x[num_args:]))


def flatten(_tuple: PypelyTuple) -> PypelyTuple:
    result = []
    if isinstance(_tuple, PypelyTuple):
        for elem in _tuple:
            if isinstance(elem, PypelyTuple):
                if any(isinstance(x, PypelyTuple) for x in elem):
                    result += list(flatten(elem))
                else:
                    result += list(elem)
            else:
                result.append(elem)
        return PypelyTuple(*result)
    raise ValueError(f"You can use flatten only with 'PypelyTuple'. Input is of type: {type(_tuple)}")


def side_effect(func: Callable):
    def __run_func(*_input):
        func(*_input)

        # TODO: find better solution
        if len(_input) == 1:
            return _input[0]
        return _input

    return lambda *x: __run_func(*x)


def optional(func: Callable, cond: bool):
    return lambda *x:  func(*x) if cond else x


head = lambda x: x[0]
last = lambda x: x[-1]
rest = lambda x: PypelyTuple(*x[1:])