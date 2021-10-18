from pypely import pipeline, fork, merge, to, identity
from pypely.helpers import optional, side_effect

from dataclasses import dataclass
from typing import Callable

import numpy as np
import torch

from ds.metric import get_accuracy_score
from ds.tracking import StageName
from ds.training import TrainingDependencies


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


def optimize(optimizer: torch.optim.Optimizer) -> Callable[[Batch], None]:
    def run_optimization(batch: Batch):
        optimizer.zero_grad()
        batch.metric.loss.backward()
        optimizer.step()

    return run_optimization


def batch(training_dependencies: TrainingDependencies, batch_data: BatchData, stage: StageName, step: int) -> Batch:
    _optimize = optional(optimize(training_dependencies.optimizer), stage == StageName.TRAIN)

    process = pipeline(
        fork(
            lambda _, batch_data: batch_data,
            run_batch,
        ),
        fork(
            identity,
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