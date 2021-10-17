from dataclasses import dataclass, field
from typing import list


@dataclass(frozen=True)
class BatchMetric:
    value: float
    batch_size: int 


@dataclass(frozen=True)
class EpochMetric:
    avg_value: float


def batches_to_epoch(batches: list[BatchMetric]) -> EpochMetric:
    total_value = sum([batch.values * batch.batch_size for batch in batches])
    total_size = sum(map(lambda batch: batch.batch_size, batches))

    avg = total_value / total_size
    return EpochMetric(avg)

