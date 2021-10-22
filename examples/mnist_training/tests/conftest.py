from pytest import fixture

import numpy as np
from typing import List
from dataclasses import dataclass, field
import torch
from collections import namedtuple
from pathlib import Path

from pypely.helpers import flatten

from mnist_training.src.ds.models import create_linear_net
from mnist_training.src.ds.dataset import create_dataloader
from mnist_training.src.ds.training import TrainingDependencies
from mnist_training.src.ds.tracking import StageName, ExperimentTracker

HERE = Path(__file__).parent.resolve()
DATA_DIR = HERE.parent


@fixture(autouse=True)
def mock_summary_writer(mocker):
    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.add_scalar',
        lambda self, tag, value, step: print(f"{tag}, {value}, {step}")
    )

    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.add_figure',
        lambda self, tag, fig, step: print(f"{tag}, {step}")
    )

    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.flush',
        lambda self: print("flushing...")
    )


@dataclass
class TestWriter:
    metrics: List[str] = field(default_factory=list)

    def add_epoch_metric(self, stage: StageName, name: str, value: float, epoch_id: int):
        self.metrics.append(f"""
            Stage: {stage.name}
            Name: {name}
            Value: {value}
            Epoch: {epoch_id}
        """)

    def add_batch_metric(self, stage: StageName, name: str, value: float, batch_id: int):
        self.metrics.append(f"""
            Stage: {stage.name}
            Name: {name}
            Value: {value}
            Batch: {batch_id}
        """)

    def add_confusion_matrix(self, stage: StageName, y_true_batches: List[np.ndarray], y_pred_batches: List[np.ndarray], epoch_id: int):
        self.metrics.append(f"""
            Stage: {stage.name}
            Y: {y_true_batches}
            Prediction: {y_pred_batches}
            Epoch: {epoch_id}
        """)

    def flush(self):
        for metric in self.metrics:
            print(f"""
                ----------------
                {metric}
                ----------------
            """)


def flush(writer: TestWriter):
    writer.flush()

def add_batch_metric(writer: TestWriter, stage: StageName, name: str, value: float, batch_id: int):
    writer.add_batch_metric(stage, name, value, batch_id)

def add_epoch_metric(writer: TestWriter, stage: StageName, name: str, value: float, epoch_id: int):
    writer.add_epoch_metric(stage, name, value, epoch_id)

def add_confusion_matrix(writer: TestWriter, stage: StageName, y_true_batches: List[np.ndarray], y_pred_batches: List[np.ndarray], epoch_id: int):
    writer.add_confusion_matrix(stage, y_true_batches, y_pred_batches, epoch_id)

def model_and_optimizer():
    return flatten(create_linear_net(torch.optim.Adam, 5e-5)())


@fixture()
def training_dependencies() -> TrainingDependencies:
    experiment = ExperimentTracker(TestWriter(), flush, add_batch_metric, add_epoch_metric, add_confusion_matrix)
    model, optimizer = model_and_optimizer()
    train_deps = TrainingDependencies(model, optimizer, torch.nn.CrossEntropyLoss(reduction="mean"), experiment)

    return train_deps


@fixture()
def test_files():
    return DATA_DIR / "data/t10k-images-idx3-ubyte.gz"


@fixture()
def test_labels():
    return DATA_DIR / "data/t10k-labels-idx1-ubyte.gz"


@fixture()
def batch_size():
    return 128


@fixture()
def minimal_dataloader(test_files, test_labels, batch_size):
    MinimalDataloader = namedtuple('MinimalDataloader', ['x', 'y'])
    data = create_dataloader(batch_size, test_files, test_labels)
    x_s = [x for x, _ in data]
    y_s = [y for _, y in data]

    return [MinimalDataloader(x_s[0], y_s[0])]