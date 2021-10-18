import torch
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from pypely import pipeline, fork, to, merge, identity
from pypely.helpers import side_effect, optional

from typing import Any, Callable, list, Iterable, Tuple
from collections import namedtuple
from dataclasses import dataclass
from functools import reduce

from .tracking import ExperimentTracker, StageName


@dataclass(frozen=True)
class TrainingDependencies:
    model: torch.nn.Module
    optimizer: torch.optim.Optimizer
    loss: torch.nn.modules.loss._Loss
    experiment: ExperimentTracker


@dataclass(frozen=True)
class BatchData:
    x: torch.Tensor
    y: torch.Tensor


@dataclass(frozen=True)
class BatchResult:
    pred: np.ndarray


@dataclass(frozen=True)
class BatchMetric:
    loss: torch.Tensor
    accuracy: float
    batch_size: int       


@dataclass(frozen=True)
class Batch:
    data: BatchData
    result: BatchResult
    metric: BatchMetric


@dataclass(frozen=True)
class StageResult:
    true: list[np.ndarray]
    pred: list[np.ndarray]


@dataclass(frozen=True)
class StageMetric:
    accuracy: float


@dataclass(frozen=True)
class Stage:
    batches: list[Batch]
    result: StageResult
    metric: StageMetric


@dataclass(frozen=True)
class Epoch:
    train: Stage
    test: Stage


def optimize(optimizer: torch.optim.Optimizer) -> Callable[[Batch], None]:
    def run_optimization(batch: Batch):
        optimizer.zero_grad()
        batch.metric.loss.backward()
        optimizer.step()

    return run_optimization


def get_accuracy_score(pred: torch.Tensor, true: torch.Tensor) -> float:
    y_np = true.detach().numpy()
    y_prediction_np = np.argmax(pred.detach().numpy(), axis=1)

    return accuracy_score(y_np, y_prediction_np)


def batch(training_dependencies: TrainingDependencies, batch_data: BatchData, stage: StageName, step: int) -> Batch:
    _optimize = optional(optimize(training_dependencies.optimizer), stage == StageName.TRAIN)

    process = pipeline(
        fork(
            lambda _, batch_data: batch_data,
            run_batch,
        ),
        fork(
            merge(lambda batch_data, _: batch_data),
            merge(lambda _, batch_result: batch_result),
            merge(batch_metric(training_dependencies.loss, get_accuracy_score))
        ),
        to(Batch),
        side_effect(_optimize),
        side_effect(lambda batch: training_dependencies.experiment.add_batch_metric(stage, "accuracy", batch.accuracy, step))
    )
    
    return process(training_dependencies.model, batch_data)


def run_batch(model: torch.nn.Module, batch_data: BatchData) -> BatchResult:
    process = pipeline(
        lambda model, batch_data: model(batch_data.x),
        lambda pred: np.argmax(pred.detach().numpy(), axis=1),
        lambda pred_np: BatchResult(pred_np)
    )

    return process(model, batch_data)


def calculate_metric(metric: Callable[[torch.Tensor, torch.Tensor], float]) -> Callable[[BatchData, BatchResult], float]:
    lambda batch_data, batch_result: metric(batch_result.pred, batch_data.y)
        

def batch_metric(*metrics: Callable[[torch.Tensor, torch.Tensor], float]) -> Callable[[BatchData, BatchResult], BatchMetric]:
    get_batch_size = lambda batch_data, _: batch_data.x.shape[0]

    return pipeline(
        fork(
            *[calculate_metric(metric) for metric in metrics],
            get_batch_size
        ),
        to(BatchMetric)
    )


def batches2stage_metric(batches: Iterable[Batch]) -> StageMetric:
    def sum_batch_metrics(first, second):
        return BatchMetric(
            loss=first.loss,
            accuracy=first.accuracy + second.accuracy * second.batch_size,
            batch_size=first.batch_size + second.batch_size
        )

    get_metrics = lambda batches: map(lambda batch: batch.metric, batches),
    sum_metrics = lambda batch_metrics: reduce(lambda first, second: sum_batch_metrics(first + second), batch_metrics, BatchMetric(torch.Tensor(0), 0, 0)),

    process = pipeline(
        get_metrics,
        sum_metrics,
        lambda summed: StageMetric(summed.accuracy / summed.batch_size)
    )

    process(batches)


def batches2stage_result(batches: Iterable[Batch]) -> StageResult:
    Memory = namedtuple('Memory', ['true', 'pred'])

    def add_to_memory(memory: Memory, batch: Batch):
        memory.true.append(batch.data.y.detach().numpy())
        memory.pred.append(batch.result.pred)

        return memory

    memory = reduce(lambda batch: add_to_memory(batch), batches, Memory(true=[], pred=[]))
    return StageResult(true=memory.true, pred=memory.pred)
    


def run_stage(training_dependencies: TrainingDependencies, stage_data: DataLoader, stage: StageName) -> Stage:
    training_dependencies.model.train(stage == StageName.TRAIN)
    get_batches = lambda: [batch(training_dependencies, BatchData(x, y), stage, step) for step, (x, y) in enumerate(tqdm(stage_data, desc=stage.name, ncols=80))]

    process = pipeline(
        get_batches,
        fork(
            identity,
            lambda batches: batches2stage_result(batches),
            lambda batches: batches2stage_metric(batches)
        ),
        to(Stage)
    )

    return process()


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