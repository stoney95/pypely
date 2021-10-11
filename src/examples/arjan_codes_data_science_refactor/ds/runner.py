from typing import Any, Callable, Tuple
import torch
import numpy as np
from sklearn.metrics import accuracy_score

from pypely import pipeline, fork, merge
from pypely.helpers import side_effect, reduce_by, flatten


def train_model(
    model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, optimizer: torch.optim.Optimizer, loss: torch.nn.modules.loss._Loss
) -> Tuple[torch.Tensor, float]:

    train = pipeline(
        reduce_by(get_prediction(train=True)),
        fork(
            merge(loss),
            merge(get_accuracy_score),
        ),
        side_effect(optimize(optimizer))
    )

    return train(model, x, y)


def test_model(
    model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, loss: torch.nn.modules.loss._Loss
) -> None:
    test = pipeline(
        reduce_by(get_prediction(train=False)),
        fork(
            merge(loss),
            merge(get_accuracy_score),
            merge(lambda _, y: y.detach.numpy()),
            merge(lambda pred, _: np.argmax(pred.detach().numpy(), axis=1)), 
        ),
        flatten
    )

    return test(model, x, y)


def get_accuracy_score(prediction: torch.Tensor, y: torch.Tensor) -> float:
    y_np = y.detach().numpy()
    y_prediction_np = np.argmax(prediction.detach().numpy(), axis=1)

    return accuracy_score(y_np, y_prediction_np)


def get_prediction(train: bool) -> Callable[[torch.nn.Module, torch.Tensor], torch.Tensor]: 
    def inner(model, x):
        model.train(train)
        return model(x)

    return inner


def optimize(optimizer: torch.optim.Optimizer) -> Callable[[torch.nn.modules.loss._Loss, Any], None]:
    def run_optimization(loss, *_):
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return run_optimization



        
