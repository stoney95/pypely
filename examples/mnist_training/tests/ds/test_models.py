from mnist_training.src.ds.models import LinearNet
from mnist_training.src.ds.dataset import create_dataloader

def test_LinearNet(test_files, test_labels):
    BATCH_SIZE = 128
    data = create_dataloader(BATCH_SIZE, test_files, test_labels)
    batches = [x for x, _ in data]
    first_batch = batches[0]

    model = LinearNet()
    prediction = model(first_batch)

    assert prediction.shape[0] == BATCH_SIZE
