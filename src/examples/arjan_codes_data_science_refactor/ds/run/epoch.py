from pypely import pipeline, fork, to
from dataclasses import dataclass
from torch.utils.data import DataLoader

from ds.training import TrainingDependencies
from ds.tracking import StageName
from ds.run.stage import run_stage, Stage


@dataclass(frozen=True)
class Epoch:
    train: Stage
    test: Stage


def run_epoch(training_dependencies: TrainingDependencies, train_data: DataLoader, test_data: DataLoader):
    train = lambda: run_stage(training_dependencies, train_data, StageName.TRAIN)
    test = lambda: run_stage(training_dependencies, test_data, StageName.TEST)

    process = pipeline(
        fork(
            train,
            test
        ),
        to(Epoch, "train", "test")
    )

    return process()