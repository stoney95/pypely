from mnist_training.src.ds.training import TrainingDependencies
from mnist_training.src.ds.tracking import StageName, ExperimentTracker

from mnist_training.src.output.metric import log_metrics

import numpy as np
from typing import List
from dataclasses import dataclass, field

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


def test_log_metric(epoch):
    experiment = ExperimentTracker(TestWriter(), flush, add_batch_metric, add_epoch_metric, add_confusion_matrix)
    train_deps = TrainingDependencies(None, None, None, experiment)

    log_metrics(epoch, 5, train_deps)
