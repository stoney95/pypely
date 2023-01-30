"""I expose functionality to persist step outputs and use them in later steps.

This functionality leverages the shift operators `>>` and `<<`. 
This allows you to store the output of a step and use it later in an other step. 
You can either use a string to define a memory entry or `pypely.memory.MemoryEntry`

Example:
```python
pipeline(
    func1 >> "result",
    func2,
    func3,
    func4 << "result"
)
```

```python
result = MemoryEntry()

pipeline(
    func1 >> result,
    func2,
    func3,
    func4 << result
)
```

The function that consumes the memory entry also consumes the output from the previous step.
So from the previous example `func4` would receive the output of `func3` **and** the memory entry `result`.

The types of the memory entries are stored and it is checked if a function is capable to consume
a memory entry based on the type information. 

> :warning: The names of memory entries must be unique throughout the code base when using strings.
This limitation is given as there is no way to identify the context in which the memory is used during buildtime.
The type information is stored during the buildtime. The simplest way to work around this limitation is to use
`pypely.memory.MemoryEntry` as shown in the second example.

> :warning: The usage of memory entries is context sensitive. This means that you can only consume memory entries
from that have been created in the same pipeline. Furthermore this means that the usage of memory entries from
 sub- / parent-pipelines is not possible. This is done to prohibit too complex memory usages. 

Due to the context sensitivity, the following example will fail:

```python
pipeline(
    func1 >> "result",
    pipeline(
        func2 << "result",
        func3,
        func4
    ),
    func5
)
```
"""

from pypely.memory.wrappers import memorizable, MemoryEntry
from pypely.memory._impl import PipelineMemory
from pypely.memory import errors

__all__ = ['PipelineMemory', 'memorizable', 'errors']