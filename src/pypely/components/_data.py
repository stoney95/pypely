from dataclasses import dataclass
from typing import Callable, List, Union


@dataclass(frozen=True)
class Fork:
    branches: List[Callable]
    parallel: bool = False

    def __eq__(self, other: 'Fork'):
        if isinstance(other, Fork):
            return _compare_list_elements(self.branches, other.branches)


@dataclass(frozen=True)
class Merge:
    func: Callable

    def __eq__(self, other: 'Merge'):
        if isinstance(other, Merge):
            return _function_equality(self.func, other.func)
        return False


@dataclass(frozen=True)
class Operation:
    func: Callable

    def __eq__(self, other: 'Operation'):
        if isinstance(other, Operation):
            return _function_equality(self.func, other.func)
        return False


MemorizableStep = Union[Fork, Merge, Operation, 'Pipeline']
Step = Union[MemorizableStep, 'Memorizable']
@dataclass(frozen=True)
class Pipeline:
    steps: List[Step]

    def __eq__(self, other: 'Pipeline'):
        if isinstance(other, Pipeline):
            return _compare_list_elements(self.steps, other.steps)


@dataclass(frozen=True)
class Memorizable:
    func: MemorizableStep

    def __eq__(self, other: 'Memorizable'):
        if isinstance(other, Memorizable):
            return self.func == other.func
        return False


def _compare_list_elements(list1, list2) -> bool:
    return all(elem1 == elem2 for (elem1, elem2) in zip(list1, list2))


def _function_equality(func1, func2):
    same_module = func1.__module__ == func2.__module__
    same_qualifier = func1.__qualname__ == func2.__qualname__
    same_call_args = _compare_list_elements(_call_args(func1), _call_args(func2))

    return same_module and same_qualifier and same_call_args


def _call_args(func):
    if func.__closure__ is None:
        return []
    return [cell.cell_contents for cell in func.__closure__]