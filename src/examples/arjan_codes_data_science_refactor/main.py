from pypely import pipeline

import torch

from .ds.load_data import load_image_data, load_label_data
from .ds.runner import train_model, test_model
from .ds.models import LinearNet

LR = 5e-5

def main():
    train_data = load_image_data("data/train-images-idx3-ubyte.gz")
    train_labes = load_image_data("data/train-labes-idx1-ubyte.gz")
    test_data = load_image_data("data/t10k-images-idx3-ubyte.gz")
    test_labes = load_image_data("data/t10k-labes-idx1-ubyte.gz")

    model = LinearNet()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    loss_function = torch.nn.CrossEntropyLoss(reduction="mean")


    trained_model = train_model(model, train_data, train_labes, optimizer, loss_function)



if __name__ == '__main__':
    main()