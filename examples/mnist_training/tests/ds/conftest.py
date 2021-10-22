from pytest import fixture

from torch.utils.tensorboard import SummaryWriter

@fixture(autouse=True)
def mock_summary_writer(mocker):
    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.add_scalar',
        lambda self, tag, value, step: print(f"{tag}, {value}, {step}")
    )

    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.add_figure',
        lambda self, tag, fig, step: print(f"{tag}, {step}")
    )

    mocker.patch(
        'torch.utils.tensorboard.SummaryWriter.flush',
        lambda self: print("flushing...")
    )


@fixture()
def writer(): 
    return SummaryWriter()