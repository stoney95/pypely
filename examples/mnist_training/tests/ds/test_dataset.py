from mnist_training.src.ds.dataset import create_dataloader

from functools import reduce
from pathlib import Path
import math

def test_create_dataloader(test_files, test_labels):
    BATCH_SIZE = 128

    test_data = create_dataloader(BATCH_SIZE, test_files, test_labels)

    batches = [(x,y) for x, y in test_data]
    assert len(batches) == math.ceil(10000 / BATCH_SIZE)

    batch_sizes = [x.shape[0] for x, _ in batches]
    count_devating_batch_sizes = reduce(lambda count, batch_size: count+1 if batch_size != BATCH_SIZE else count, batch_sizes, 0)
    assert count_devating_batch_sizes <= 1
