# Helpers
The helpers module provide useful functions that can be used inside a pipeline. If these functions don't fit your need you can easily create your own. Provided functions are:

  - [reduce_by](#reduce_by)
  - [flatten](#flatten)
  - [side_effect](#side_effect)
  - [optional](#optional)
  - [head](#head)
  - [last](#last)
  - [rest](#rest)

Additionally to this document you can see the [tests](https://github.com/stoney95/pypely/tree/main/tests/test_helpers.py).

## reduce_by
`reduce_by` applies the given `Callable` to as many arguments as this takes and returns a `Tuple` with the return value of the given `Callable` at the first position followed by the remaining arguments.

> **Signature** `(func: Callable[[*args], T]) -> Callable[[*args, *remaining], Tuple[T, *remaining]]`<br>
> **Import** `from pypely.helpers import reduce_by`

### Inputs
`reduce_by` takes a `Callable` that consumes `*args` and outputs `T`.

### Outputs
`reduce_by` produces a `Callable` that consumes `*args` and an unlimited number of optional arguments `*remaining` and outputs a `Tuple` with `T` at the first position followed by `*remaining`.


## flatten
`flatten` takes a (nested) `PypelyTuple` and returns a flat (not nested) `PypelyTuple`.

> **Signature** (_tuple: PypelyTuple) -> PypelyTuple <br>
> **Import** `from pypely.helpers import flatten`

### Inputs
A `PypelyTuple` that can have multiple levels.

### Outputs
A flat `PypelyTuple` with a single level


## side_effect
`side_effect` runs the given function without transforming the intermediate result. This could be used for e.g. logging, sending metrics to a metric server or other side effects. By using this function a step in a `pipeline` is clearly marked as performing a side effect.

> **Signature** `(func: Callable[[T], Any]) -> Callable[[T], T]`<br>
> **Import** `from pypely.helpers import side_effect`

### Inputs
`side_effect` takes a function that consumes the intermediate result. 

### Outputs
`side_effect` outputs a `Callable` that consumes the intermediate result and outputs it without transforming it. 


## optional
`optional` makes it possible to run a function depending on the input. If the given condition is not met the intermediate result will be forwarded. 

> **Signature** `(func: Callable[[IN], OUT], cond: Callable[..., bool]) -> Callable[[IN], Union[IN, OUT]]`<br>
> **Import** `from pypely.helpers import optional`

### Inputs
`optional` takes two `Callable`s. The first one is the function that may be applied to the intermediate result `IN`. The second one is function that indicates wheter the function should be exectued or not. `IN` is applied to `cond` but it is wrapped with `reduce_by`. So `cond` needs to take any number of arguments in [0, len(IN)]. 

Example: 
```python
def add(x, y):
    return x + y

optional_add = optional(add, cond=lambda x: x > 10)
```
Here `add` takes two arguments. The `Callable` given for `cond` only takes a single argument. These usages would also be possible:

```python
optional_add = optional(add, cond=lambda: True)
optional_add = optional(add, cond=lambda x, y: x*y < 4)
```

Whereas this results in an error:
```python
optional_add = optional(add, cond=lambda x, y, z: x * y + z > 10)
```

### Outputs
A `Callable` that consumes the intermediate result `IN` and depending on `cond` outputs `IN` or the result of `func` `OUT`.

## head
Takes a list and returns the first element.

> **Signature** `(x: Iterable[T]) -> T`<br>
> **Import** `from pypely.helpers import head`


## last
Takes a list and returns the last element.

> **Signature** `(x: Iterable[T]) -> T`<br>
> **Import** `from pypely.helpers import last`


## rest
Takes a list and returns the list without the first element.

> **Signature** `(x: Iterable[T]) -> Iterable[T]`<br>
> **Import** `from pypely.helpers import rest`
