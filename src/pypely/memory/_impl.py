from typing import Optional, Any

class PipelineMemory:
    def __init__(self):
        print("Memory created")

    def add(self, name: str, value: Any) -> None:
        self.__setattr__(name, value)

    def get(self, name: str) -> Any:
        try:
            return self.__getattribute__(name)
        except AttributeError:
            raise AttributeError(
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