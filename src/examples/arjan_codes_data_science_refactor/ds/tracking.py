from dataclasses import dataclass
import numpy as np
from typing import Callable, TypeVar, list, Generic

Writer = TypeVar("Writer")


@dataclass(frozen=True)
class ExperimentTracker(Generic[Writer]):
    writer: Writer
    flush: Callable[[Writer], None]
    add_batch_metric: Callable[[Writer, str, str, float, int], None]
    add_epoch_metric: Callable[[Writer, str, str, float, int], None]
    add_confusion_matrix: Callable[[Writer, str, list[np.ndarray], list[np.ndarray], int], None]
