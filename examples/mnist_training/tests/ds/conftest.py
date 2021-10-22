from pytest import fixture
from pathlib import Path
from mnist_training.src.ds.tracking import StageName

from torch.utils.tensorboard import SummaryWriter



@fixture()
def writer(): 
    return SummaryWriter()


@fixture()
def stage_name():
    return StageName.TEST
