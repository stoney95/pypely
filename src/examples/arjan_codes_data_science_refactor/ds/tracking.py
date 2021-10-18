from dataclasses import dataclass
import numpy as np
from typing import Callable, TypeVar, List, Generic
from enum import Enum, auto

Writer = TypeVar("Writer")


class StageName(Enum):
    TRAIN = auto()
    TEST = auto()
    VAL = auto()


#TODO: how could the writer be ingested? Inheritance, property, decorator?
@dataclass(frozen=True)
class ExperimentTracker(Generic[Writer]):
    __writer: Writer
    __flush: Callable[[Writer], None]
    __add_batch_metric: Callable[[Writer, StageName, str, float, int], None]
    __add_epoch_metric: Callable[[Writer, StageName, str, float, int], None]
    __add_confusion_matrix: Callable[[Writer, StageName, List[np.ndarray], List[np.ndarray], int], None]


    def flush(self):
        self.__flush(self.__writer)

    def add_batch_metric(self, stage: StageName, name: str, value: float, step: int):
        self.__add_batch_metric(self.__writer, stage, name, value, step)

    def add_epoch_metric(self, stage: StageName, name: str, value: float, epoch_id: int):
        self.__add_epoch_metric(self.__writer, stage, name, value, epoch_id)

    def add_confusion_matrix(self, stage: StageName, y_true_batches: List[np.ndarray], y_pred_batches: List[np.ndarray], epoch_id: int):
        self.__add_confusion_matrix(self.__writer, stage, y_true_batches, y_pred_batches, epoch_id)