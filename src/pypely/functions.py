from functools import reduce
from typing import Callable, Any, List
from inspect import getfullargspec
from collections.abc import Iterable



def pipeline(*funcs: Callable) -> Callable:
    def _reducer(func1, func2):
        try:
            return lambda *x: func2(func1(*x))
        except Exception as e:
            raise e

    return reduce(_reducer, funcs)


def fork(*funcs: Callable) -> Callable:
    return lambda *x: [func(*x) for func in funcs]


def merge(func: Callable) -> Callable:
    return lambda branches: func(*flatten(branches))
    # return lambda branches: reduce(lambda x, y: func(x, y), branches)


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


def partial_apply(func: Callable) -> Callable:
    num_args = len(getfullargspec(func).args)
    return lambda *x: (func(*x[:num_args]), x[num_args:])


identity = lambda x: x