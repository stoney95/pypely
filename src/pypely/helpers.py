from typing import Callable, List, Any, Tuple
from inspect import getfullargspec


def reduce_by(func: Callable) -> Callable:
    num_args = len(getfullargspec(func).args)
    return lambda *x: (func(*x[:num_args]), x[num_args:])


def flatten(_tuple: Tuple[Any]) -> Tuple[Any]:
    result = []
    for elem in _tuple:
        if isinstance(elem, Tuple):
            if any(isinstance(x, Tuple) for x in elem):
                result += flatten(elem)
            else:
                result += elem
        else:
            result.append(elem)

    return tuple(result)


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
rest = lambda x: x[1:]