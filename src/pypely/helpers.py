from typing import Callable, List, Any, Iterable
from inspect import getfullargspec


def reduce_by(func: Callable) -> Callable:
    num_args = len(getfullargspec(func).args)
    return lambda *x: (func(*x[:num_args]), x[num_args:])


def flatten(_list: List[Any]) -> List[Any]:
    result = []
    for elem in _list:
        if isinstance(elem, Iterable):
            if any(isinstance(x, Iterable) for x in elem):
                result += flatten(elem)
            else:
                result += elem
        else:
            result.append(elem)

    return result


def side_effect(func: Callable):
    def __run_func(*_input):
        func(*_input)
        return _input

    return lambda *x: __run_func(*x)


def optional(func: Callable, cond: bool):
    return lambda *x:  func(*x) if cond else x


head = lambda x: x[0]
last = lambda x: x[-1]
rest = lambda x: x[1:]