from pypely import pipeline, fork, to
from dataclasses import dataclass
from torch.utils.data import DataLoader
from typing import Callable, Iterable

from ds.training import TrainingDependencies
from ds.tracking import StageName
from ds.run.stage import run_stage, Stage


@dataclass(frozen=True)
class EpochData:
    train: DataLoader
    test: DataLoader


@dataclass(frozen=True)
class Epoch:
    train: Stage
    test: Stage


def run_epoch(training_dependencies: TrainingDependencies, epoch_data: EpochData) -> Epoch:
    train = lambda: run_stage(training_dependencies, epoch_data.train, StageName.TRAIN)
    test = lambda: run_stage(training_dependencies, epoch_data.test, StageName.TEST)

    process = pipeline(
        fork(
            train,
            test
        ),
        to(Epoch, "train", "test")
    )

    return process()


def run_epochs(epochs: int) -> Callable[[TrainingDependencies, EpochData], Iterable[Epoch]]:
    def _inner(training_dependencies: TrainingDependencies, epoch_data: EpochData) -> Iterable[Epoch]:
        for _ in range(epochs):
            yield run_epoch(training_dependencies, epoch_data)
    
    return _inner