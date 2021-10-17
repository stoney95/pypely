from pypely import pipeline

from pathlib import Path
from typing import Any, Tuple, List
from dataclasses import dataclass

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from .load_data import load_image_data, load_label_data

TRAIN_MAX = 255.0
TRAIN_NORMALIZED_MEAN = 0.1306604762738429
TRAIN_NORMALIZED_STDEV = 0.3081078038564622


@dataclass(frozen=True)
class MNIST(Dataset):
    x: List[torch.Tensor]
    y: List[torch.Tensor]

    def __post_init__(self):
        assert len(self.x) == len(self.y)

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x = self.x[idx]
        y = self.y[idx]

        return x, y


def preprocess_data(data: np.ndarray) -> List[torch.Tensor]:
    preprocess = pipeline(
        lambda x: x / TRAIN_MAX,
        lambda x: x - TRAIN_NORMALIZED_MEAN,
        lambda x: x / TRAIN_NORMALIZED_STDEV,
        lambda x: x.astype(np.float32),
        lambda x: torch.from_numpy(x),
        lambda x: x.unsqueeze(0)
    )

    return [preprocess(x.copy().astype(np.float64)) for x in data]


def preprocess_labels(labels: np.ndarray) -> List[torch.Tensor]:
    preprcess = lambda y: torch.tensor(y, dtype=torch.long)
    return [preprcess(y) for y in labels]


def create_dataloader(
    batch_size: int, data_path: Path, label_path: Path, shuffle: bool = True
) -> DataLoader[Any]:

    data = load_image_data(data_path)
    labels = load_label_data(label_path)

    x = preprocess_data(data)
    y = preprocess_labels(labels)

    return DataLoader(
        dataset=MNIST(x, y),
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
    )
