import pytest

def pytest_sessionstart(session, mocker):
    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.add_scalar',
        lambda tag, value, step: print(f"{tag}, {value}, {step}")
    )

    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.add_figure',
        lambda tag, fig, step: print(f"{tag}, {step}")
    )

    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.flush',
        lambda: print("flushing...")
    )