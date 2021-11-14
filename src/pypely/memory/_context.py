from pypely.memory._impl import get_memory, set_memory, PipelineMemory


class PipelineMemoryContext:
    previous_memory: PipelineMemory = None

    def __enter__(self):
        self.previous_memory = get_memory()
        set_memory(PipelineMemory())

    def __exit__(self, type, value, traceback):
        set_memory(self.previous_memory)
