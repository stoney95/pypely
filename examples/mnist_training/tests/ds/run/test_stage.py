from mnist_training.src.ds.run.stage import run_stage
import numpy as np


def test_run_stage(training_dependencies, minimal_dataloader, stage_name):
    stage_result = run_stage(training_dependencies, minimal_dataloader, stage_name)

    assert len(stage_result.result.true) == len(minimal_dataloader)
    assert len(stage_result.result.pred) == len(minimal_dataloader)

    assert len(stage_result.batches) == len(minimal_dataloader)
    assert type(stage_result.metric.accuracy) == np.float64