from mnist_training.src.ds.training import TrainingDependencies
from mnist_training.src.ds.tracking import StageName
from mnist_training.src.ds.run.epoch import Epoch


def log_metrics(epoch: Epoch, i: int, training_dependencies: TrainingDependencies):
    experiment = training_dependencies.experiment

    experiment.add_epoch_metric(StageName.TRAIN, "accuracy", epoch.train.metric.accuracy, i)
    experiment.add_epoch_metric(StageName.TEST, "accuracy", epoch.test.metric.accuracy, i)
    experiment.add_confusion_matrix(StageName.TEST, epoch.test.result.true, epoch.test.result.pred, i)

    experiment.flush()