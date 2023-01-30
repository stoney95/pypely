# import uuid

# from dataclasses import dataclass, field
# from typing import Callable, List, Optional, Union


# @dataclass(frozen=True)
# class Step:
#     id: uuid.UUID = field(default_factory=uuid.uuid4)


# @dataclass(frozen=True)
# class Fork(Step):
#     branches: List[Step] = field(default_factory=list)
#     parallel: bool = False

#     def __eq__(self, other: 'Fork'):
#         if isinstance(other, Fork):
#             return _compare_list_elements(self.branches, other.branches)


# @dataclass(frozen=True)
# class Merge(Step):
#     func: Callable=None

#     def __eq__(self, other: 'Merge'):
#         if isinstance(other, Merge):
#             return _function_equality(self.func, other.func)
#         return False


# @dataclass(frozen=True)
# class Operation(Step):
#     func: Callable=None

#     def __eq__(self, other: 'Operation'):
#         if isinstance(other, Operation):
#             return _function_equality(self.func, other.func)
#         return False


# @dataclass(frozen=True)
# class Pipeline(Step):
#     steps: List[Step] = field(default_factory=list)

#     def __eq__(self, other: 'Pipeline'):
#         if isinstance(other, Pipeline):
#             return _compare_list_elements(self.steps, other.steps)


# @dataclass(frozen=True)
# class Memorizable(Step):
#     func: Step = None
#     read_attributes: List[str]=field(default_factory=list)
#     write_attribute: Optional[str] = None

#     def __eq__(self, other: 'Memorizable'):
#         if isinstance(other, Memorizable):
#             return self.func == other.func
#         return False


# def _compare_list_elements(list1, list2) -> bool:
#     return all(elem1 == elem2 for (elem1, elem2) in zip(list1, list2))


# def _function_equality(func1, func2):
#     same_module = func1.__module__ == func2.__module__
#     same_qualifier = func1.__qualname__ == func2.__qualname__
#     same_call_args = _compare_list_elements(_call_args(func1), _call_args(func2))

#     return same_module and same_qualifier and same_call_args


# def _call_args(func):
#     if func.__closure__ is None:
#         return []
#     return [cell.cell_contents for cell in func.__closure__]