from typing import Callable, TypeVar, Any, Union
from inspect import getfullargspec
from ._types import PypelyTuple

T = TypeVar("T")
IN = TypeVar("IN")
OUT = TypeVar("OUT")


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


def side_effect(func: Callable[[T], Any]) -> Callable[[T], T]:
    def __run_func(*_input):
        func(*_input)

        # TODO: find better solution
        if len(_input) == 1:
            return _input[0]
        return _input

    return lambda *x: __run_func(*x)


def optional(func: Callable[[IN], OUT], cond: Callable[..., bool]) -> Callable[[IN], Union[IN, OUT]]:
    # TODO: add custom error if cond takes more arguments than func
    def __inner(*x):
        _cond = reduce_by(cond)(*x)[0]
        if _cond:
            return func(*x)
        else:
            return x

    return __inner


head = lambda x: x[0]
last = lambda x: x[-1]
rest = lambda x: PypelyTuple(*x[1:])