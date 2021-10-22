from mnist_training.src.output.metric import log_metrics

def test_log_metric(epoch, training_dependencies):
    log_metrics(epoch, 5, training_dependencies)
