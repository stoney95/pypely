from pypely import pipeline, fork, to, identity, merge
from pypely.functions import T
from pypely.helpers import side_effect, reduce_by

import torch
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
from datetime import datetime

from ds.dataset import create_dataloader
from ds.models import LinearNet
from ds.tracking import ExperimentTracker
from ds.training import TrainingDependencies
from ds.run.epoch import run_epochs, EpochData, Epoch
from output import log_metrics, print_summary
import ds.tensorboard as tb_tracking

LR = 5e-5
EPOCHS = 20
BATCH_SIZE = 128

HERE = Path(__file__).parent.resolve()
LOG_DIR = HERE.parent.parent.parent / "runs" / datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = HERE.parent / "data"
TRAIN_DATA = DATA_DIR / "train-images-idx3-ubyte.gz"
TRAIN_LABELS = DATA_DIR / "train-labels-idx1-ubyte.gz"
TEST_DATA = DATA_DIR / "t10k-images-idx3-ubyte.gz"
TEST_LABELS = DATA_DIR / "t10k-labels-idx1-ubyte.gz"


create_model = pipeline(
    lambda: LinearNet(),
    fork(
        identity,
        lambda model: torch.optim.Adam(model.parameters(), lr=LR)
    )
)

create_training_dependencies = pipeline(
    fork(
        create_model,
        lambda: torch.nn.CrossEntropyLoss(reduction="mean"),
        lambda: ExperimentTracker[SummaryWriter](SummaryWriter(log_dir=str(LOG_DIR)), tb_tracking.flush, tb_tracking.add_batch_metric, tb_tracking.add_epoch_metric, tb_tracking.add_epoch_confusion_matrix),
    ),
    to(TrainingDependencies)
)


create_epoch_data = pipeline(
    fork(
        lambda: create_dataloader(BATCH_SIZE, TRAIN_DATA, TRAIN_LABELS),
        lambda: create_dataloader(BATCH_SIZE, TEST_DATA, TEST_LABELS),
    ),
    to(EpochData)
)


log_epoch =fork(
    log_metrics,
    print_summary(EPOCHS)
)


log_epochs = lambda epochs, training_dependencies: [log_epoch(epoch, i, training_dependencies) for i, epoch in enumerate(epochs)]


main = pipeline(
    fork(
        create_training_dependencies,
        create_epoch_data
    ),
    fork(
        merge(run_epochs(EPOCHS)),
        merge(lambda training_dependencies, _: training_dependencies),
    ),
    merge(log_epochs)
)

if __name__ == '__main__':
    main()