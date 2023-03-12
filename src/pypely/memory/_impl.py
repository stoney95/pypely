"""I implement the `PipelineMemory`.

This class is used to store outputs of steps. 
It also stores the types at buildtime.
"""

from typing import Any, Optional, Type

from pypely.memory.errors import InvalidMemoryAttributeError, MemoryAttributeExistsError, MemoryAttributeNotFoundError


class PipelineMemory:
    """I store the memorized values."""

    types: dict[str, type]

    def __init__(self) -> None:
        self.types = dict()

    def add(self, name: str, value: Any) -> None:
        """I add a value to the memory.

        Args:
            name (str): The name of the memory entry.
            value (Any): The stored value

        Raises:
            MemoryAttributeExistsError: if an entry with the given name already exists.
        """
        if name in self.__dict__.keys():
            raise MemoryAttributeExistsError(f"The attribute {name} already exists")
        self.__setattr__(name, value)

    def get(self, name: str) -> Any:
        """I retrieve the entry with the given `name`.

        Args:
            name (str): The name of the memory entry.

        Returns:
            Any: the value corresponding to the name.

        Raises:
            MemoryAttributeNotFoundError: if there is no memory entry with the given name.
        """
        try:
            return self.__getattribute__(name)
        except AttributeError:
            raise MemoryAttributeNotFoundError(
                f"""Tried to access attribute {name} but attribute was not found. 
                Available Attributes: {list(self.__dict__.keys())}"""
            )

    def add_type(self, name: str, _type: Type) -> None:
        """I add a type to the type memory.

        Args:
            name (str): The name of the memory entry.
            _type (Type): The type of the memory entry.

        Raises:
            MemoryAttributeExistsError: if there is already an entry with `name`
            InvalidMemoryAttributeError: if the type is not supported by the memory. E.g. `None`.
        """
        if name in self.types.keys():
            raise MemoryAttributeExistsError(f"The attribute {name} already exists")

        if _type == type(None) or _type == None:
            raise InvalidMemoryAttributeError(
                f"It is not allowed to store `None` in memory. Given memory attribute name: {name}"
            )
        self.types[name] = _type

    def get_type(self, name: str) -> type:
        """I provide the type of the memory entry belonging to `name`.

        This is used during buildtime. The stored types are used to check if a memory entry can be ingested into a function.

        Args:
            name (str): The name of the memory entry.

        Raises:
            MemoryAttributeNotFoundError: if there is no memory entry with the given name.

        Returns:
            type: the type of the memory entry.
        """
        try:
            return self.types[name]
        except KeyError:
            raise MemoryAttributeNotFoundError(
                f"""Tried to access type information of attribute {name}. Attribute was not found. 
                Available attribute types: {list(self.types.keys())}"""
            )


MEMORY: Optional[PipelineMemory] = None


def get_memory() -> PipelineMemory:
    """I store the globally available memory.

    Returns:
        PipelineMemory: the global state of the memory.
    """
    global MEMORY
    if MEMORY is None:
        MEMORY = PipelineMemory()
    return MEMORY


def set_memory(memory: PipelineMemory) -> None:
    """I set the given `memory` as the globally available memory.

    Args:
        memory (PipelineMemory): the memory that should be set as the global memory.
    """
    global MEMORY
    MEMORY = memory
