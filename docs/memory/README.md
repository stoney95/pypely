# Memory

The memory module enables you to store intermediate results, that you need in a later pipeline step. This helps you to make the pipelines more readable.

The following snippet is taken from the [mnist example](https://github.com/stoney95/tree/main/examples/mnist_training/src/main.py). The first snippet was the implementation before `pypely.memory` has been introduced:
```python
    run = pipeline(
        fork(
            create_training_dependencies,
            create_epoch_data
        ),
        fork(
            merge(run_epochs(EPOCHS)),
            merge(lambda training_dependencies, _: training_dependencies),
        ),
        merge(log_epochs)
    )
```

With the introduction of `pypely.memory` the `training_dependencies` which need to be reused in the last step can be stored in the memory and be retrieved afterwards.
```python
    _create_training_dependencies = add_to_memory("training_dependencies", create_training_dependencies)
    _log_epochs = with_memory_attribute("training_dependencies", log_epochs)
    _run_epochs = run_epochs(EPOCHS)

    run = pipeline(
        fork(
            _create_training_dependencies,
            create_epoch_data
        ),
        merge(_run_epochs),
        _log_epochs
    )
```

## add_to_memory

> **Signature** `(name: str, func: Callable[..., T]) -> Callable[..., T]` <br>
> **Import** `from pypely.memory import add_to_memory`

The function `addd_to_memory` can be used to wrap a pipeline step. By this the result of the wrapped step will be stored in the memory and can be accessed by the given name. The scope of the memory is the pipeline it is defined in. This also means that the memory can not be accessed in sub pipelines. You can take a look at the [tests](https://github.com/stoney95/pypely/tree/main/tests/test_memory.py).

### Inputs
The output of the pipeline step `func` will be stored in the memory and is accessible by the given `name`.

### Outputs
By wrapping a pipeline step with `add_to_memory`, you do not modify its output. Therefore the output of the function is a `Callable` with the same signature as the given `func`. 