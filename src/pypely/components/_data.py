from dataclasses import dataclass, field
from typing import Callable, List, Union



@dataclass(frozen=True)
class Fork:
    branches: List[Callable]
    parallel: bool = False


@dataclass(frozen=True)
class Merge:
    func: Callable


@dataclass(frozen=True)
class Operation:
    func: Callable


Step = Union[Fork, Merge, Operation, 'Pipeline']
@dataclass(frozen=True)
class Pipeline:
    steps: List[Step]