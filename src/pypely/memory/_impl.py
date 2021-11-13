from typing import Optional, Any
from pypely.memory.errors import MemoryAttributeExistsError, MemoryAttributeNotFoundError

class PipelineMemory:
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


MEMORY: Optional[PipelineMemory] = None

def get_memory() -> PipelineMemory:
    global MEMORY
    if MEMORY is None:
        MEMORY = PipelineMemory()
    return MEMORY


def set_memory(memory: PipelineMemory) -> None:
    global MEMORY
    MEMORY = memory