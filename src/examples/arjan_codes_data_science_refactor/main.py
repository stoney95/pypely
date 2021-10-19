from pypely import pipeline, fork, to, identity, merge
from pypely.helpers import side_effect, reduce_by

import torch
from typing import Any, Iterable
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path

from ds.dataset import create_dataloader
from ds.models import LinearNet
from ds.tracking import ExperimentTracker, StageName
from ds.training import TrainingDependencies
from ds.run.epoch import run_epoch, EpochData, Epoch
import ds.tensorboard as tb_tracking

LR = 5e-5
EPOCHS = 20
BATCH_SIZE = 128

HERE = Path(__file__).parent

DATA_DIR = HERE / "data"
TRAIN_DATA = DATA_DIR / "train-images-idx3-ubyte.gz"
TRAIN_LABELS = DATA_DIR / "train-labels-idx1-ubyte.gz"
TEST_DATA = DATA_DIR / "t10k-images-idx3-ubyte.gz"
TEST_LABELS = DATA_DIR / "t10k-labels-idx1-ubyte.gz"


create_model = pipeline(
    lambda: LinearNet(),
    fork(
        identity,
        lambda model: torch.optim.Adam(model.parameters(), lr=LR)
    )
)

create_training_dependencies = pipeline(
    fork(
        create_model,
        lambda: torch.nn.CrossEntropyLoss(reduction="mean"),
        lambda: ExperimentTracker[SummaryWriter](SummaryWriter(), tb_tracking.flush, tb_tracking.add_batch_metric, tb_tracking.add_epoch_metric, tb_tracking.add_epoch_confusion_matrix),
    ),
    to(TrainingDependencies)
)


create_epoch_data = pipeline(
    fork(
        lambda: create_dataloader(BATCH_SIZE, TRAIN_DATA, TRAIN_LABELS),
        lambda: create_dataloader(BATCH_SIZE, TEST_DATA, TEST_LABELS),
    ),
    to(EpochData)
)


def print_summary(epoch: Epoch, epoch_id: int, *_: Any) -> None:
    summary = ", ".join(
        [
            f"[Epoch: {epoch_id + 1}/{EPOCHS}]",
            f"Test Accuracy: {epoch.test.metric.accuracy: 0.4f}",
            f"Train Accuracy: {epoch.train.metric.accuracy: 0.4f}",
        ]
    )
    print("\n" + summary + "\n")


def log_metrics(epoch: Epoch, i: int, training_dependencies: TrainingDependencies):
    experiment = training_dependencies.experiment

    experiment.add_epoch_metric(StageName.TRAIN, "accuracy", epoch.train.metric.accuracy, i)
    experiment.add_epoch_metric(StageName.TEST, "accuracy", epoch.test.metric.accuracy, i)
    experiment.add_confusion_matrix(StageName.TEST, epoch.test.result.true, epoch.test.result.pred, i)

    experiment.flush()


def run_epochs(training_dependencies: TrainingDependencies, epoch_data: EpochData) -> Iterable[Epoch]:
    for __name__ in range(EPOCHS):
        yield run_epoch(training_dependencies, epoch_data)


def log_epoch(epoch: Epoch, epoch_id: int, training_dependencies: TrainingDependencies):
    log_metrics(epoch, epoch_id, training_dependencies)
    print_summary(epoch, epoch_id)


log_epochs = lambda epochs, training_dependencies: [log_epoch(epoch, i, training_dependencies) for i, epoch in enumerate(epochs)]


main = pipeline(
    fork(
        create_training_dependencies,
        create_epoch_data
    ),
    fork(
        merge(run_epochs),
        merge(lambda training_dependencies, _: training_dependencies),
    ),
    merge(log_epochs)
)

if __name__ == '__main__':
    main()