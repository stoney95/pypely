from typing import Optional, Any
from pypely.memory.errors import MemoryAttributeExistsError, MemoryAttributeNotFoundError, InvalidMemoryAttributeError

class PipelineMemory:
    types: dict[str, type]

    def __init__(self) -> None:
        self.types = dict()

    def add(self, name: str, value: Any) -> None:
        if name in self.__dict__.keys():
            raise MemoryAttributeExistsError(f"The attribute {name} already exists")
        self.__setattr__(name, value)

    def get(self, name: str) -> Any:
        try:
            return self.__getattribute__(name)
        except AttributeError:
            raise MemoryAttributeNotFoundError(
                f"""Tried to access attribute {name} but attribute was not found. 
                Available Attributes: {list(self.__dict__.keys())}"""
            )


    def add_type(self, name: str, _type: type) -> None:
        """I add a type to the type memory.

        Args:
            name (str): The name of the memory entry.
            _type (Type): The type of the memory entry.
        """
        if name in self.types.keys():
            raise MemoryAttributeExistsError(f"The attribute {name} already exists")

        if _type == type(None):
            raise InvalidMemoryAttributeError(f"It is not allowed to store `None` in memory. Given memory attribute name: {name}")
        self.types[name] = _type

    def get_type(self, name: str) -> type:
        try:
            return self.types[name]
        except KeyError:
            raise MemoryAttributeNotFoundError(
                f"""Tried to access type information of attribute {name}. Attribute was not found. 
                Available attribute types: {list(self.types.keys())}"""
            )


MEMORY: Optional[PipelineMemory] = None

def get_memory() -> PipelineMemory:
    global MEMORY
    if MEMORY is None:
        MEMORY = PipelineMemory()
    return MEMORY


def set_memory(memory: PipelineMemory) -> None:
    global MEMORY
    MEMORY = memory