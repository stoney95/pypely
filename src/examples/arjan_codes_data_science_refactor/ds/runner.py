import torch
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from pypely import pipeline, fork, to, merge, identity
from pypely.helpers import side_effect, optional

from typing import Any, Callable, list, Iterable, Tuple
from collections import namedtuple
from dataclasses import dataclass, field, asdict
from functools import partial, reduce

from .metric import BatchMetric, EpochMetric, batches_to_epoch
from .tracking import ExperimentTracker, StageName

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
class BatchData:
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
class StageResult:
    metric: EpochMetric
    y_true_batches: list[np.ndarray] = field(default_factory=list)
    y_pred_batches: list[np.ndarray] = field(default_factory=list)


#TODO: is code duplicated?
#TODO: naming, what is epoch, what is batch? What is inbetween? Which data is created / passed
#TODO: scoping, what is part of an epoch run / batch run? What should be handeled in a higher level?
def run_epoch(epoch: Epoch) -> Epoch:
    train_stage = StageName.TRAIN
    test_stage = StageName.VAL

    train = partial(train_model, optimizer=epoch.optimizer, loss=epoch.loss_function)
    add_batch_metric = lambda metric, value, step: epoch.experiment.add_batch_metric(train_stage, metric, value, step)
    epoch_train = run_stage(epoch.model, epoch.train_batches, train, "Train Batches", add_batch_metric)

    test = partial(test_model, loss=epoch.loss_function)
    add_batch_metric = lambda metric, value, step: epoch.experiment.add_batch_metric(test_stage, metric, value, step)
    epoch_test = run_stage(epoch.model, epoch.test_batches, test, "Validation Batches", add_batch_metric)

    epoch.experiment.add_epoch_metric(train_stage, "accuracy", epoch_train.metric.avg_value, epoch.id)
    epoch.experiment.add_epoch_metric(test_stage, "accuracy", epoch_test.metric.avg_value, epoch.id)
    epoch.experiment.add_confusion_matrix(epoch.experiment.__writer, test_stage, epoch_test.y_true_batches, epoch_test.y_pred_batches, epoch.id)

    return Epoch(
        **asdict(epoch),
        test_accuracy=epoch_test.metric.avg_value, 
        train_accuracy=epoch_train.metric.avg_value
    )


def run_stage(
    model: torch.nn.Module, 
    batches: DataLoader, 
    batch_func: Callable[[torch.nn.Module, BatchData], BatchResult], 
    desc: str,
    add_batch_metric: Callable[[str, float, int], None]
) -> StageResult:

    add_metric_to_result = lambda batch_result, batch_size: BatchResult(**asdict(batch_result), metric=BatchMetric(batch_result.accuracy, batch_size))

    def run_batch(model, x, y, step):
        batch = BatchData(x, y)
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
        to(StageResult)
    )

    return as_epoch(batches)


def train_model(
    model: torch.nn.Module, batch: BatchData, optimizer: torch.optim.Optimizer, loss: torch.nn.modules.loss._Loss
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
    model: torch.nn.Module, batch: BatchData, loss: torch.nn.modules.loss._Loss
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


def forward(train: bool) -> Callable[[BatchData], PredictionWithLabels]: 
    def inner(model: torch.nn.Module, batch: BatchData):
        model.train(train)
        prediction = model(batch.x)

        return PredictionWithLabels(prediction=prediction, label=batch.y)

    return inner





@dataclass(frozen=True)
class TrainingDependencies:
    model: torch.nn.Module
    optimizer: torch.optim.Optimizer
    loss: torch.nn.modules.loss._Loss
    experiment: ExperimentTracker


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
            merge(get_batch_metric(training_dependencies.loss))
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
    lambda batch_data, batch_result: metric(batch_result.infered_data, batch_data.y)
        

def get_batch_metric(loss: torch.optim.Optimizer) -> Callable[[BatchData, BatchResult], BatchMetric]:
    get_batch_size = lambda batch_data, _: batch_data.x.shape[0]

    return pipeline(
        fork(
            calculate_metric(loss),
            calculate_metric(get_accuracy_score),
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
    get_batches = lambda: [batch(training_dependencies, BatchData(x, y), stage, step) for step, (x, y) in enumerate(stage_data)]

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