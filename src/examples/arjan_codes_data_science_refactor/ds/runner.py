import torch
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from pypely import pipeline, fork, to
from pypely.helpers import side_effect

from typing import Any, Callable, list, Iterable, Tuple
from collections import namedtuple
from dataclasses import dataclass, field, asdict
from functools import partial

from .metric import BatchMetric, EpochMetric, batches_to_epoch
from .tracking import ExperimentTracker, Stage

#TODO: renaming
PredictionWithLabels = namedtuple('PredictionWithLabels', ["prediction", "label"])


@dataclass(frozen=True)
class Epoch:
    experiment: ExperimentTracker
    train_batches: DataLoader
    test_batches: DataLoader
    model: torch.nn.Module
    optimizer: torch.optim.Optimizer
    loss_function: torch.nn.modules.loss._Loss
    id: int = 0
    test_accuracy: float = 0.0
    train_accuracy: float = 0.0


@dataclass(frozen=True)
class Batch:
    x: torch.Tensor
    y: torch.Tensor


@dataclass(frozen=True)
class BatchResult:
    loss: float
    accuracy: float
    metric: BatchMetric
    y_true_batch: np.ndarray = field(default_factory=np.array([]))
    y_pred_batch: np.ndarray = field(default_factory=np.array([]))


@dataclass(frozen=True)
class EpochResult:
    metric: EpochMetric
    y_true_batches: list[np.ndarray] = field(default_factory=list)
    y_pred_batches: list[np.ndarray] = field(default_factory=list)


#TODO: is code duplicated?
def run_epoch(epoch: Epoch) -> Epoch:
    train_stage = Stage.TRAIN
    test_stage = Stage.VAL

    train = partial(train_model, optimizer=epoch.optimizer, loss=epoch.loss_function)
    add_batch_metric = lambda metric, value, step: epoch.experiment.add_batch_metric(epoch.experiment.writer, train_stage, metric, value, step)
    epoch_train = run_batches(epoch.model, epoch.train_batches, train, "Train Batches", add_batch_metric)

    test = partial(test_model, loss=epoch.loss_function)
    add_batch_metric = lambda metric, value, step: epoch.experiment.add_batch_metric(epoch.experiment.writer, test_stage, metric, value, step)
    epoch_test = run_batches(epoch.model, epoch.test_batches, test, "Validation Batches", add_batch_metric)

    epoch.experiment.add_epoch_metric(epoch.experiment.writer, train_stage, "accuracy", epoch_train.metric.avg_value, epoch.id)
    epoch.experiment.add_epoch_metric(epoch.experiment.writer, test_stage, "accuracy", epoch_test.metric.avg_value, epoch.id)
    epoch.experiment.add_confusion_matrix(epoch.experiment.writer, test_stage, epoch_test.y_true_batches, epoch_test.y_pred_batches, epoch.id)

    return Epoch(
        **asdict(epoch),
        test_accuracy=epoch_test.metric.avg_value, 
        train_accuracy=epoch_train.metric.avg_value
    )


def run_batches(
    model: torch.nn.Module, 
    batches: Iterable[Tuple[torch.Tensor, torch.Tensor]], 
    batch_func: Callable[[Batch], BatchResult], 
    desc: str,
    add_batch_metric: Callable[[str, float, int], None]
) -> EpochResult:

    add_metric_to_result = lambda batch_result, batch_size: BatchResult(**asdict(batch_result), metric=BatchMetric(batch_result.accuracy, batch_size))

    def run_batch(model, x, y, step):
        batch = Batch(x, y)
        batch_result = batch_func(model, batch)
        add_batch_metric("accuracy", batch_result.accuracy, step)
        
        return add_metric_to_result(batch_result, x.shape[0])

    get_batch_results = lambda batches: [run_batch(model, x, y, i) for i, (x, y) in enumerate(tqdm(batches, ncols=80, desc=desc))]

    as_epoch = pipeline(
        get_batch_results,
        fork(
            lambda batch_results: batches_to_epoch([batch.metric for batch in batch_results]),
            lambda batch_results: [batch.y_true_batch for batch in batch_results],
            lambda batch_results: [batch.y_pred_batch for batch in batch_results]
        ),
        to(EpochResult)
    )

    return as_epoch(batches)


def train_model(
    model: torch.nn.Module, batch: Batch, optimizer: torch.optim.Optimizer, loss: torch.nn.modules.loss._Loss
) -> BatchResult:

    train = pipeline(
        forward(train=True),
        fork(
            loss,
            get_accuracy_score,
        ),
        to(BatchResult, "loss", "accuracy"),
        side_effect(optimize(optimizer))
    )

    return train(model, batch)


def test_model(
    model: torch.nn.Module, batch: Batch, loss: torch.nn.modules.loss._Loss
) -> BatchResult:

    label_to_numpy = lambda data: data.y.detach.numpy()
    predicted_label_as_numpy = lambda data: np.argmax(data.prediction.detach().numpy(), axis=1)

    test = pipeline(
        forward(train=False),
        fork(
            loss,
            get_accuracy_score,
            label_to_numpy,
            predicted_label_as_numpy,
        ),
        to(BatchResult, "loss", "accuracy", "y_true_batch", "y_pred_batch")
    )

    return test(model, batch)


def get_accuracy_score(data: PredictionWithLabels) -> float:
    y_np = data.y.detach().numpy()
    y_prediction_np = np.argmax(data.prediction.detach().numpy(), axis=1)

    return accuracy_score(y_np, y_prediction_np)


def forward(train: bool) -> Callable[[Batch], PredictionWithLabels]: 
    def inner(model: torch.nn.Module, batch: Batch):
        model.train(train)
        prediction = model(batch.x)

        return PredictionWithLabels(prediction=prediction, label=batch.y)

    return inner


def optimize(optimizer: torch.optim.Optimizer) -> Callable[[BatchResult], None]:
    def run_optimization(batch_result: BatchResult):
        optimizer.zero_grad()
        batch_result.loss.backward()
        optimizer.step()

    return run_optimization



        
