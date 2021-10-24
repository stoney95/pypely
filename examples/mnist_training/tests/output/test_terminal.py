from mnist_training.src.output import print_summary

def test_print_summary(epoch):
    executable = print_summary(epochs=10)
    executable(epoch, 4)
