from pypely import pipeline, fork, to
from dataclasses import dataclass
from torch.utils.data import DataLoader

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