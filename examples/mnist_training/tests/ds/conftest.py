from pytest import fixture
import tempfile
from mnist_training.src.ds.tracking import StageName


from torch.utils.tensorboard import SummaryWriter



@fixture()
def writer():
    with tempfile.TemporaryDirectory() as tmp: 
        return SummaryWriter(log_dir=tmp)


@fixture()
def stage_name():
    return StageName.TEST
