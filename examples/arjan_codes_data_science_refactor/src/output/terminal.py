from typing import Callable, Any

from ds.run.epoch import Epoch

def print_summary(epochs: int) -> Callable[[Epoch, int, Any], None]:
    def _inner(epoch: Epoch, epoch_id: int, *_: Any) -> None:
        summary = ", ".join(
            [
                f"[Epoch: {epoch_id + 1}/{epochs}]",
                f"Test Accuracy: {epoch.test.metric.accuracy: 0.4f}",
                f"Train Accuracy: {epoch.train.metric.accuracy: 0.4f}",
            ]
        )
        print("\n" + summary + "\n")
    
    return _inner