import pytest
import numpy as np

from mnist_training.src.ds.run.epoch import Epoch
from mnist_training.src.ds.run.stage import Stage, StageMetric, StageResult


@pytest.fixture()
def epoch():
    stage_result = StageResult(
        true=[np.array([1, 2, 3, 4])],
        pred=[np.array([1, 2, 3, 4])],
    )

    stage_metric = StageMetric(
        accuracy=1.0
    )

    stage = Stage([], stage_result, stage_metric)
    epoch = Epoch(train=stage, test=stage)

    return epoch