from pypely import pipeline, fork, to, identity, merge
from pypely.helpers import side_effect, reduce_by

import torch
from typing import Any
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

DATA_DIR = Path("data")
TRAIN_DATA = DATA_DIR / "data/train-images-idx3-ubyte.gz"
TRAIN_LABELS = DATA_DIR / "data/train-labels-idx1-ubyte.gz"
TEST_DATA = DATA_DIR / "data/t10k-images-idx3-ubyte.gz"
TEST_LABELS = DATA_DIR / "data/t10k-labels-idx1-ubyte.gz"


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


def log_epoch(epoch: Epoch, i: int, training_dependencies: TrainingDependencies):
    experiment = training_dependencies.experiment

    experiment.add_epoch_metric(StageName.TRAIN, "accuracy", epoch.train.metric.accuracy, i)
    experiment.add_epoch_metric(StageName.TEST, "accuracy", epoch.test.metric.accuracy, i)
    experiment.add_confusion_matrix(StageName.TEST, epoch.test.result.true, epoch.test.result.pred, i)

    experiment.flush()

#TODO: increase readability with iterator
epoch = pipeline(
    fork(
        reduce_by(run_epoch),
        lambda training_dependencies, *_: training_dependencies, 
    ),
    side_effect(merge(log_epoch)),
    side_effect(merge(print_summary)),
)

epochs = lambda training_dependencies, epoch_data: [epoch(training_dependencies, epoch_data, i) for i in range(EPOCHS)]

main = pipeline(
    fork(
        create_training_dependencies,
        create_epoch_data
    ),
    merge(epochs)
)

if __name__ == '__main__':
    main()