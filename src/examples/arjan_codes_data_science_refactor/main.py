from pypely import pipeline, fork, to, identity
from pypely.helpers import side_effect

import torch
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
from dataclasses import asdict

from ds.dataset import create_dataloader
from ds.runner import run_epoch, Epoch
from ds.models import LinearNet
from ds.tracking import ExperimentTracker
from ds.tensorboard import *

LR = 5e-5
EPOCHS = 20
BATCH_SIZE = 128

DATA_DIR = Path("data")
TRAIN_DATA = DATA_DIR / "data/train-images-idx3-ubyte.gz"
TRAIN_LABELS = DATA_DIR / "data/train-labels-idx1-ubyte.gz"
TEST_DATA = DATA_DIR / "data/t10k-images-idx3-ubyte.gz"
TEST_LABELS = DATA_DIR / "data/t10k-labels-idx1-ubyte.gz"


create_model = pipeline(
    lambda: LinearNet(), 
    fork(
        identity,
        lambda model: torch.optim.Adam(model.parameters(), lr=LR),
    )
)


#TODO: move this to runner.run_epoch
flush_writer = lambda epoch: epoch.experiment.flush(epoch.experiment.writer)
print_summary = lambda epoch: print(f"\nEpoch: {epoch.id}/{EPOCHS}, Test Accuracy: {epoch.test_accuracy: 0.4f}, Train Accuracy: {epoch.train_accuracy: 0.4}\n")

epoch_summary = pipeline(
    run_epoch,
    side_effect(print_summary),
    flush_writer
)

run_epochs = lambda epoch: [epoch_summary(Epoch(**asdict(epoch), id=i)) for i in range(EPOCHS)]

main = pipeline(
    fork(
        lambda: ExperimentTracker[SummaryWriter](SummaryWriter(), flush, add_batch_metric, add_epoch_metric, add_epoch_confusion_matrix),
        lambda: create_dataloader(BATCH_SIZE, TRAIN_DATA, TRAIN_LABELS),
        lambda: create_dataloader(BATCH_SIZE, TEST_DATA, TEST_LABELS),
        lambda: create_model,
        lambda: torch.nn.CrossEntropyLoss(reduction="mean")
    ),
    to(Epoch, "experiment", "train_batches", "test_batches", "model", "optimizer", "loss_function"),
    run_epochs
)


if __name__ == '__main__':
    main()