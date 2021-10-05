from dataclasses import dataclass, field
from typing import List, Any

@dataclass(frozen=True)
class Me():
    position: str
    hungry: bool
    awake: bool = False
    preparing: Any = None

    def __repr__(self):
        emotion = ""
        if self.awake:
            if self.hungry:
                emotion ="😒"
            else:
                emotion ="😋"
        else:
            emotion ="😴"

        __repr = f"{emotion} in the {self.position}"
        if self.preparing:
            __repr += f" while preparing {self.preparing}"
        return __repr


@dataclass(frozen=True)
class Tea(): 
    def __repr__(self):
        return "🍵"

    def __str__(self):
        return self.__repr__()


@dataclass(frozen=True)
class Bread():
    def __repr__(self):
        return "🍞"
    
    def __str__(self):
        return self.__repr__()


@dataclass(frozen=True)
class Eggs():
    def __repr__(self):
        return "🍳"

    def __str__(self):
        return self.__repr__()


@dataclass(frozen=True)
class Plate():
    def __repr__(self):
        return "🍽️"

    def __str__(self):
        return self.__repr__()

@dataclass(frozen=True)
class Table():
    objects_on_table: List[Any] = field(default_factory=lambda: [])

    @property
    def is_set(self):
        plate_on_table = any(type(obj) == Plate for obj in self.objects_on_table)
        at_least_3_elements = len(self.objects_on_table) >= 3

        return (plate_on_table & at_least_3_elements)

    def __repr__(self):
        if self.is_set:
            return f"table set with: {' '.join([str(obj) for obj in self.objects_on_table])}"
        return "empty table"

