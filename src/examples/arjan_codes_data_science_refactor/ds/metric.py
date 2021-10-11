from dataclasses import dataclass, field
from typing import list


@dataclass(frozen=True)
class Metric:
    values: list[float] = field(default_factory=list)
    running_total: float = 0.0
    num_updates: float = 0.0
    average: float = 0.0


def update(metric: Metric, value: float, batch_size: int):
    running_total = value * batch_size
    num_updates = metric.num_updates + batch_size
    average = running_total / num_updates

    return Metric(
        values=metric.values.append(value),
        running_total=running_total,
        num_updates=num_updates,
        average=average,
    )