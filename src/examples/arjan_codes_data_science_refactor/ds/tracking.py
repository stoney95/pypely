from dataclasses import dataclass
import numpy as np
from typing import Callable, TypeVar, List, Generic
from enum import Enum, auto

Writer = TypeVar("Writer")


class Stage(Enum):
    TRAIN = auto()
    TEST = auto()
    VAL = auto()


@dataclass(frozen=True)
class ExperimentTracker(Generic[Writer]):
    writer: Writer
    flush: Callable[[Writer], None]
    add_batch_metric: Callable[[Writer, Stage, str, float, int], None]
    add_epoch_metric: Callable[[Writer, Stage, str, float, int], None]
    add_confusion_matrix: Callable[[Writer, Stage, List[np.ndarray], List[np.ndarray], int], None]
