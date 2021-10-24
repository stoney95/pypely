from typing import List
from torch.utils.tensorboard import SummaryWriter
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import numpy as np

from .tracking import StageName


def flush(writer: SummaryWriter):
    writer.flush()


def add_batch_metric(writer: SummaryWriter, stage: StageName, name: str, value: float, step: int):
    tag = f"{stage.name}/batch/{name}"
    writer.add_scalar(tag, value, step)


def add_epoch_metric(writer: SummaryWriter, stage: StageName, name: str, value: float, step: int):
    tag = f"{stage.name}/epoch/{name}"
    writer.add_scalar(tag, value, step)


def add_epoch_confusion_matrix(writer: SummaryWriter, stage: StageName, y_true: List[np.ndarray], y_pred: List[np.ndarray], step: int):
    def _collapse_batch(batch_list: List[np.ndarray]) -> np.ndarray:
        return np.concatenate(batch_list)

    def _create_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> plt.Figure:
        cm = ConfusionMatrixDisplay(confusion_matrix(y_true, y_pred)).plot(cmap="Blues")
        cm.ax_.set_title(f"{stage.name} Epoch: {step}")
        return cm.figure_

    y_true = _collapse_batch(y_true)
    y_pred = _collapse_batch(y_pred)

    fig = _create_confusion_matrix(y_true, y_pred)
    tag = f"{stage.name}/epoch/confusion_matrix"
    writer.add_figure(tag, fig, step)



