"""I take care of providing the right memory for each context.

Sub-pipelines don't have access to parent pipelines and vic-versa.
"""

from pypely.memory._impl import PipelineMemory, get_memory, set_memory


class PipelineMemoryContext:
    """I switch between memories depending on the context."""

    previous_memory: PipelineMemory

    def __enter__(self) -> None:
        """I provide a freshly initialized memory.

        The current memory is stored for later usage.
        """
        self.previous_memory = get_memory()
        set_memory(PipelineMemory())

    def __exit__(self, type, value, traceback) -> None:
        """I reset the memory to the previous one.

        # noqa: DAR101
        """
        set_memory(self.previous_memory)
