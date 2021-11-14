# Memory

The memory module enables you to store intermediate results, that you need in a later pipeline step. This helps you to make the pipelines more readable.

> :warning: If you have to use the `memory` a lot you should rethink the design of the data flow in your application! The memory module is ment to enable a bypass in some situations. It should not appear in every `pipeline` you create. 

The following snippet is taken from the [mnist example](https://github.com/stoney95/tree/main/examples/mnist_training/src/main.py). The first snippet was the implementation before `pypely.memory` has been introduced:
```python
    run = pipeline(
        fork(
            create_training_dependencies,
            create_epoch_data
        ),
        fork(
            merge(run_epochs(NUM_EPOCHS)),
            merge(lambda training_dependencies, _: training_dependencies),
        ),
        merge(log_epochs)
    )
```

The training dependencies are created in the first step and need to be available in the last step to log the epochs. The second `fork` is only relevant to forward the training dependencies. This makes the code less readable.
With the introduction of `pypely.memory` the `training_dependencies` can be stored in the memory and be retrieved afterwards.
```python
    from pypely.memory import memorizable

    _create_training_dependencies = memorizable(create_training_dependencies)
    _log_epochs = memorizable(log_epochs)

    run = pipeline(
        fork(
            _create_training_dependencies >> "training_dependencies",
            create_epoch_data
        ),
        merge(run_epochs(NUM_EPOCHS)),
        _log_epochs << "training_dependencies"
    )
```

## memorizable

> **Signature** `(func: Optional[Callable[..., T]]=None, allow_ingest: Optional[bool]=True) -> Union[Memorizable, Callable[..., T]]` <br>
> **Signature AddOn** `Memorizable = Callable([Callable[..., T]], Callable[..., T])`<br>
> **Import** `from pypely.memory import memorizable`

The function `memorizable` can be used to wrap a pipeline step. By this the result of the wrapped step can be stored in the memory by adding 

```python
pipeline_step >> "<name_in_memory>"
```

Additionally this step can consume objects stored in the memory. This can be done by 

```python
"<name_in_memory>" >> pipeline_step << "<name_in_memory>"
```

`"<name_in_memory>" >> pipeline_step` will ingest the object in the memory before the intermediate result. The signature of `pipeline_step` should look like this: `(object_from_memory, intermediate_result)`. 
Respectively `pipeline_step << "<name_in_memory>"` will ingest the object after the intermediate result. The signature should look like this: `(intermediate_result, object_from_memory)`. In the snippet above both ways are applied. The signature of `pipeline_step` should look like: `(object_from_memory, intermediate_result, object_from_memory)`

It is also possible to ingest multiple memory objects: 
```python
pipeline_step << "<name_in_memory_1>" << "<name_in_memory_2>"
```

The scope of the memory is the `pipeline` it is defined in. This especially means that the memory can not be accessed in sub pipelines or parent pipelines. You can take a look at the [tests](https://github.com/stoney95/pypely/tree/main/tests/test_memory.py) for detailed information.

### Usage
`memorizable` can be used as a decorator or inline wrapper. In both ways it is possible to allow or prohibit the ingestion of memory objects for given function. When memory ingestion is not allowed the result of the function can be stored in the memory. The function itself can **not** consume any objects from the memory.

#### Decorator
```python
from pypely.memory import memorizable

@memorizable
def func_that_can_consume_memory_objects():
    ...

@memorizable(allow_ingest=False)
def func_that_can_only_write_to_memory():
    ...
```

#### Inline Wrapper
```python
def func_1():
    ...

func_that_can_consume_memory_objects = memorizable(func_1)
func_that_can_only_write_to_memory = memorizable(func_1, allow_ingest=False)
```


#### Usage in a `pipeline`

```python
from pypely import pipeline

run = pipeline(
    func_that_can_only_write_to_memory >> "my_result",
    ...
    func_that_can_consume_memory_objects << "my_result",
    ...
    func_that_can_only_write_to_memory << "my_result" # <-- This will fail as memory ingestion has benn disabled
)
```