from mnist_training.src.ds.metric import get_accuracy_score
import torch
import numpy as np

def test_get_accuracy_score():
    pred = np.zeros((8,8))
    np.fill_diagonal(pred, 1)

    '''
    content of pred:
    [
        [1,0,0,0,0,0,0,0]
        [0,1,0,0,0,0,0,0]
        [0,0,1,0,0,0,0,0]
        [0,0,0,1,0,0,0,0]
        [0,0,0,0,1,0,0,0]
        [0,0,0,0,0,1,0,0]
        [0,0,0,0,0,0,1,0]
        [0,0,0,0,0,0,0,1]
    ]
    '''

    y_true = torch.from_numpy(np.array([0,1,2,3,4,5,6,7]))
    y_pred = torch.from_numpy(pred)

    accuracy = get_accuracy_score(y_pred, y_true)

    assert accuracy == 1.0