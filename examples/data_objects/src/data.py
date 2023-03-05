"""I provide example data classes."""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass(frozen=True)
class Me:
    """noqa: D101."""

    position: str
    hungry: bool
    awake: bool = False
    preparing: Any = None

    def __repr__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        emotion = ""
        if self.awake:
            if self.hungry:
                emotion = "😒"
            else:
                emotion = "😋"
        else:
            emotion = "😴"

        __repr = f"{emotion} in the {self.position}"
        if self.preparing:
            __repr += f" while preparing {self.preparing}"
        return __repr


@dataclass(frozen=True)
class Tea:
    """noqa: D101."""

    def __repr__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return "🍵"

    def __str__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.__repr__()


@dataclass(frozen=True)
class Bread:
    """noqa: D101."""

    def __repr__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return "🍞"

    def __str__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.__repr__()


@dataclass(frozen=True)
class Eggs:
    """noqa: D101."""

    def __repr__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return "🍳"

    def __str__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.__repr__()


@dataclass(frozen=True)
class Plate:
    """noqa: D101."""

    def __repr__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return "🍽️"

    def __str__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.__repr__()


@dataclass(frozen=True)
class Table:
    """noqa: D101."""

    objects_on_table: List[Any] = field(default_factory=lambda: [])

    @property
    def is_set(self):
        """noqa: D102.

        # noqa: DAR101
        # noqa: DAR201
        """
        plate_on_table = any(type(obj) == Plate for obj in self.objects_on_table)
        at_least_3_elements = len(self.objects_on_table) >= 3

        return plate_on_table & at_least_3_elements

    def __repr__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        if self.is_set:
            return f"table set with: {' '.join([str(obj) for obj in self.objects_on_table])}"
        return "empty table"
