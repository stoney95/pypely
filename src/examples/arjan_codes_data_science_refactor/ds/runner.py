from typing import Any, Callable, list, Iterable, Tuple
import torch
import numpy as np
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from pypely import pipeline, fork, to, merge
from pypely.helpers import side_effect, select

from collections import namedtuple
from dataclasses import dataclass, field, asdict
from functools import partial

from .metric import BatchMetric, EpochMetric, batches_to_epoch

#TODO: renaming
RawInput = namedtuple('RawInput', ["model", "x", "y"])
PredictionWithLabels = namedtuple('PredictionWithLabels', ["prediction", "label"])


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


def run_epoch(model, batches, optimizer, loss):
    train = partial(train_model, optimizer=optimizer, loss=loss)
    epoch_train = run_batches(model, batches, train, "Train Batches")

    test = partial(test_model, loss=loss)
    epoch_test = run_batches(model, batches, test, "Validation Batches")

    #TODO: experiment.add_epoch_metric("accuracy", epoch_avg_accuracy, epoch_id)
    #TODO: experiment.add_epoch_metric("accuracy", epoch_avg_accuracy, epoch_id)
    #TODO: experiment.add_confusion_matrix(y_true_batches, y_pred_batchs, epoch_id)


def run_batches(
    model: torch.nn.Module, 
    batches: Iterable[Tuple[torch.Tensor, torch.Tensor]], 
    batch_func: Callable[[torch.nn.Module, torch.Tensor, torch.Tensor], BatchResult], 
    desc: str
) -> EpochResult:

    batch_size = lambda model, x, y: x.shape[0]
    add_metric_to_result = lambda batch_result, batch_size: BatchResult(**asdict(batch_result), metric=BatchMetric(batch_result.accuracy, batch_size))

    run_batch = pipeline(
        fork(
            batch_func,
            batch_size
        ),
        merge(add_metric_to_result)
        # TODO: side_effect(add_batch_metric)
    )

    batch_results: list[BatchResult] = [run_batch(model, x, y) for x, y in tqdm(batches, ncols=80, desc=desc)]

    gather_epoch = pipeline(
        fork(
            lambda batch_results: batches_to_epoch([batch.metric for batch in batch_results]),
            lambda batch_results: [batch.y_true_batch for batch in batch_results],
            lambda batch_results: [batch.y_pred_batch for batch in batch_results]
        ),
        to(EpochResult)
    )

    return gather_epoch(batch_results)


def train_model(
    model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, optimizer: torch.optim.Optimizer, loss: torch.nn.modules.loss._Loss
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

    raw_input = RawInput(model, x, y)
    return train(raw_input)


def test_model(
    model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, loss: torch.nn.modules.loss._Loss
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

    raw_input = RawInput(model, x, y)
    return test(raw_input)


def get_accuracy_score(data: PredictionWithLabels) -> float:
    y_np = data.y.detach().numpy()
    y_prediction_np = np.argmax(data.prediction.detach().numpy(), axis=1)

    return accuracy_score(y_np, y_prediction_np)


def forward(train: bool) -> Callable[[RawInput], PredictionWithLabels]: 
    def inner(raw_input: RawInput):
        raw_input.model.train(train)
        prediction = raw_input.model(raw_input.x)

        return PredictionWithLabels(prediction=prediction, label=raw_input.y)

    return inner


def optimize(optimizer: torch.optim.Optimizer) -> Callable[[BatchResult], None]:
    def run_optimization(batch_result: BatchResult):
        optimizer.zero_grad()
        batch_result.loss.backward()
        optimizer.step()

    return run_optimization



        
