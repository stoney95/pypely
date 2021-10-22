import torch

from dataclasses import dataclass
from mnist_training.src.ds.tracking import ExperimentTracker


@dataclass(frozen=True)
class TrainingDependencies:
    model: torch.nn.Module
    optimizer: torch.optim.Optimizer
    loss: torch.nn.modules.loss._Loss
    experiment: ExperimentTracker
    