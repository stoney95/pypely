from pypely import pipeline, fork, to, identity
from dataclasses import dataclass
from typing import List, Iterable
from torch.utils.data import DataLoader
from tqdm import tqdm
from functools import reduce
from collections import namedtuple

import numpy as np
import torch

from mnist_training.src.ds.tracking import StageName
from mnist_training.src.ds.training import TrainingDependencies
from mnist_training.src.ds.run.batch import batch, Batch, BatchData, BatchMetric


@dataclass(frozen=True)
class StageResult:
    true: List[np.ndarray]
    pred: List[np.ndarray]


@dataclass(frozen=True)
class StageMetric:
    accuracy: float


@dataclass(frozen=True)
class Stage:
    batches: List[Batch]
    result: StageResult
    metric: StageMetric


def run_stage(training_dependencies: TrainingDependencies, stage_data: DataLoader, stage: StageName) -> Stage:
    training_dependencies.model.train(stage == StageName.TRAIN)
    get_batches = lambda: [batch(training_dependencies, BatchData(x, y), stage, step) for step, (x, y) in enumerate(tqdm(stage_data, desc=stage.name, ncols=80))]

    process = pipeline(
        get_batches,
        fork(
            identity,
            batches2stage_result,
            batches2stage_metric
        ),
        to(Stage)
    )

    return process()


def batches2stage_metric(batches: Iterable[Batch]) -> StageMetric:
    def sum_batch_metrics(first, second):
        return BatchMetric(
            loss=first.loss,
            accuracy=first.accuracy + second.accuracy * second.batch_size,
            batch_size=first.batch_size + second.batch_size
        )

    get_metrics = lambda batches: map(lambda batch: batch.metric, batches)
    sum_metrics = lambda batch_metrics: reduce(lambda first, second: sum_batch_metrics(first, second), batch_metrics, BatchMetric(torch.Tensor(0), 0, 0))
    get_average = lambda summed_metric: summed_metric.accuracy / summed_metric.batch_size

    process = pipeline(
        get_metrics,
        sum_metrics,
        get_average,
        lambda avg: StageMetric(avg)
    )

    return process(batches)


def batches2stage_result(batches: Iterable[Batch]) -> StageResult:
    Memory = namedtuple('Memory', ['true', 'pred'])

    def _add_to_memory(memory: Memory, batch: Batch):
        memory.true.append(batch.data.y.detach().numpy())
        memory.pred.append(np.argmax(batch.result.pred.detach().numpy(), axis=1))

        return memory

    memory = reduce(lambda memory, batch: _add_to_memory(memory, batch), batches, Memory(true=[], pred=[]))
    return StageResult(true=memory.true, pred=memory.pred)
    