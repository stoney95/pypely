from mnist_training.src.ds.tensorboard import flush, add_batch_metric, add_epoch_metric, add_epoch_confusion_matrix
from mnist_training.src.ds.tracking import StageName

import numpy as np


def test_flush(writer):
    flush(writer)


def test_add_batch_metric(writer): 
    add_batch_metric(writer, StageName.TRAIN, "accuracy", 0.5, 4)


def test_add_epoch_metric(writer): 
    add_epoch_metric(writer, StageName.TRAIN, "accuracy", 0.5, 4)


def test_add_confusion_matrix(writer): 
    add_epoch_confusion_matrix(writer, StageName.TRAIN, [np.array([1,2,3,4])], [np.array([1,2,3,4])], 4)
