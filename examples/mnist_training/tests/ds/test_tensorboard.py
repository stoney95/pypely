from mnist_training.src.ds.tensorboard import flush
from torch.utils.tensorboard import SummaryWriter





def test_flush():
    writer = SummaryWriter()
    flush(writer)
