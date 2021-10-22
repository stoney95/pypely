import numpy as np
from sklearn.metrics import accuracy_score
import torch


def get_accuracy_score(pred: torch.Tensor, true: torch.Tensor) -> float:
    y_np = true.detach().numpy()
    y_prediction_np = np.argmax(pred.detach().numpy(), axis=1)

    return accuracy_score(y_np, y_prediction_np)
