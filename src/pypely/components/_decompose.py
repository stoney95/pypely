from pypely.components._data import Pipeline, Fork, Merge, Operation
from pypely.core._debug_helpers import DebugMemory


def _is(_type):
    def inner(func):
        is_from_core_modul = func.__module__ == "pypely.core.functions"
        is_type = func.__qualname__.startswith(_type)

        return is_type and is_from_core_modul
    
    return inner

is_pipeline = _is("pipeline")
is_fork = _is("fork")
is_merge = _is("merge")


def decompose(pipe):
    if is_pipeline(pipe):
        inside_pipeline = pipe.__closure__[0].cell_contents.__closure__
        last_step = inside_pipeline[1].cell_contents

        debug_memory = inside_pipeline[0].cell_contents
        first_steps = _traverse(debug_memory)
        steps = [*first_steps, last_step]
        return Pipeline(steps=[decompose(step) for step in steps])
    if is_fork(pipe):
        parallel_steps = pipe.__closure__[0].cell_contents
        return Fork([decompose(step) for step in parallel_steps])
    if is_merge(pipe):
        return Merge(func=pipe.__closure__[0].cell_contents)
    else:
        return Operation(func=pipe)


def _traverse(debug_memory: DebugMemory, memory=None):
    if memory is None:
        memory = []

    if debug_memory.combine != debug_memory.first:
        new_debug_memory = debug_memory.combine.__closure__[0].cell_contents
        memory.append(debug_memory.last)
        return _traverse(new_debug_memory, memory)
    else:
        memory.append(debug_memory.first)
        return reversed(memory)