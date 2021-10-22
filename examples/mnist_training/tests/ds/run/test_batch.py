import pytest
from mnist_training.src.ds.run.batch import optimize, batch, Batch, BatchData, BatchResult, BatchMetric
from mnist_training.src.ds.training import TrainingDependencies

from mnist_training.src.ds.tracking import StageName

import torch
import numpy as np


def test_optimize(batch_size, minimal_dataloader, training_dependencies: TrainingDependencies):
    model = training_dependencies.model
    optimizer = training_dependencies.optimizer
    loss_function = training_dependencies.loss

    mini_batch = minimal_dataloader[0]
    x = mini_batch.x
    y = mini_batch.y

    pred = model(x)

    loss = loss_function(pred, y)

    batch_data = BatchData(x, y)
    batch_result = BatchResult(pred)
    batch_metric = BatchMetric(loss, 0.5, batch_size)

    batch = Batch(batch_data, batch_result, batch_metric)

    optimization = optimize(optimizer)
    optimization(batch)


def test_batch(batch_size, minimal_dataloader, training_dependencies: TrainingDependencies):
    mini_batch = minimal_dataloader[0]
    x = mini_batch.x
    y = mini_batch.y

    batch_data = BatchData(x, y)
    batch_result = batch(training_dependencies, batch_data, StageName.TEST, 1)

    assert batch_result.result.pred.shape[0] == batch_size
    assert batch_result.metric.batch_size == batch_size
    assert torch.equal(batch_result.data.x, x)
    assert torch.equal(batch_result.data.y, y)
    assert type(batch_result.metric.accuracy) == np.float64