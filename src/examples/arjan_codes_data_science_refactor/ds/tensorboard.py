from typing import list
from torch.utils.tensorboard import SummaryWriter
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import numpy as np


def flush(writer: SummaryWriter):
    writer.flush()


def add_batch_metric(writer: SummaryWriter, stage: str, name: str, value: float, step: int):
    tag = f"{stage}/batch/{name}"
    writer.add_scalar(tag, value, step)


def add_epoch_metric(writer: SummaryWriter, stage: str, name: str, value: float, step: int):
    tag = f"{stage}/epoch/{name}"
    writer.add_scalar(tag, value, step)


def add_epoch_confusion_matrix(writer: SummaryWriter, stage: str, y_true: list[np.ndarray], y_pred: list[np.ndarray], step: int):
    def _collapse_batch(batch_list: list[np.ndarray]) -> np.ndarray:
        return np.concatenate(batch_list)

    def _create_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> plt.Figure:
        cm = ConfusionMatrixDisplay(confusion_matrix(y_true, y_pred))
        cm.ax_.set_title(f"{stage} Epoch: {step}")
        return cm

    y_true = _collapse_batch(y_true)
    y_pred = _collapse_batch(y_pred)

    fig = _create_confusion_matrix(y_true, y_pred)
    tag = f"{stage}/epoch/confusion_matrix"
    writer.add_figure(tag, fig, step)



