from mnist_training.src.ds.run.epoch import run_epoch, run_epochs, EpochData
from typing import Iterable


def test_run_epoch(minimal_dataloader, training_dependencies):
    epoch_data = EpochData(minimal_dataloader, minimal_dataloader)
    epoch_result = run_epoch(training_dependencies, epoch_data)

    assert len(epoch_result.test.result.pred) == len(minimal_dataloader)


def test_run_epochs(minimal_dataloader, training_dependencies):
    num_epochs = 1
    epoch_runner = run_epochs(num_epochs)
    epoch_data = EpochData(minimal_dataloader, minimal_dataloader)

    epochs = epoch_runner(training_dependencies, epoch_data)

    assert len(list(epochs)) == num_epochs
    