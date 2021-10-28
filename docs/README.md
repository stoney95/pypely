# Documentation
This is the official documentation for `pypely`. This page will describe the core functions and how they can be applied. Please also see the documentation for:

* [helpers](localhost:3000/#/helpers/)

## Core functions
This section will describe the core functions:

* [pipeline](#pipeline)
* [fork](#fork)
* [merge](#merge)
* [to](#to)
* [identity](#identity)

Additionally to this document you can take a look at the [tests](https://github.com/stoney95/pypely/tree/main/tests/test_functions.py)

### `pipeline`

> **Signature** `(*func: Callable) -> Callable` <br>
> **Import** `from pypely import pipeline`

`pipeline` allows you to chain defined functions together. The output of a function will be passed as the input to the following function. `pipeline` can be used like the following:

```python
use_pypely = pipeline(
    open_favourite_ide,
    create_new_conda_environment,
    activate_environment,
    install_pypely,
    have_fun_building_pipelines 
)

use_pypely() # -> 🥳
```

#### Inputs
The number of inputs is not defined for `pipeline` as you can chain as many functions as you like. But each input needs to be a `Callable`. This includes using a `lambda` expression directly inside `pipeline`. Using `lambda` can be useful but don't use it to often as this will decrease readability.

Demonstration:  
```python
def add(x, y):
    return x + y

def print_result(result):
    print(result)

# Valid usages
valid_1 = pipeline(add)
valid_2 = pipeline(add, print_result)
valid_3 = pipeline(add, lambda result: print(result))
valid_4 = pipeline(add, print)
valid_4 = pipeline(add, identity, identity, identity, identity, print)

# Invalid usages
x = 1
y = 2
invalid_1 = pipeline(4, 2, add)
invalid_2 = pipeline((4, 2), add)
invalid_3 = pipeline(x, y, add)
invalid_4 = pipeline(add, x, y)
```

Using invalid arguments will currently not produce an error when creating the pipeline. The error will be thrown when executing the pipeline. This will be addressed in [this issue](https://github.com/stoney95/pypely/issues/4)

#### Outputs
`pipeline` will transform all the input `Callable`s into a single `Callable`. The returned `Callable` has the same signature as the first function for the input and as the last function for the output

Demonstration: 
```python
def add(x: int, y: int) -> int:
    return x + y

def add_to_3(x: int) -> int:
    return x + 3

def mul_with_5(x: int) -> int:
    return x * 5

def div_by_2(x: int) -> float:
    return x / 2

# pipe: Callable[[int, int], float]
pipe = pipeline(add, mul_with_5, add_to_3, div_by_2)
result = pipe(1,2) # result: float
```

### `fork`

> **Signature** `(*func: Callable[[T], Any]) -> Callable[[T], PypelyTuple]` <br>
> **Import** `from pypely import fork`

Sometimes you want to do multiple things with one intermediate result. `fork` allows you to do this. You can specify multiple functions inside `fork`. Each will receive the output of the previous function as the input. `fork` outputs a `PypelyTuple` with the result of each specified function in the order of the functions. You can use fork like this.

```python
morning_routine = pipeline(
    wake_up,
    go_to_kitchen,
    fork(
        make_tea,
        fry_eggs,
        cut_bread,
        get_plate
    )
)

morning_routine() # -> PypelyTuple(🍵, 🍳, 🍞, 🍽️)
```

#### Inputs
The number of inputs to `fork` is not limited as you can fork an intermediate result as often as required. But each `Callable` needs to have the same signature regarding the input, as each given `Callable` consumes the same intermediate result of type `T`.

#### Outputs
`fork` outputs a new `Callable` that consumes an intermediate result of type `T`. The output of this new `Callable` is a `PypelyTuple` with each output of the given `Callables` at the position they were given to `fork`. 

### Merge

> **Signature** `(func: [Callable[..., T]) -> Callable[[PypelyTuple], T]` <br>
> **Import** `from pypely import merge`

After you split your process into multiple branches, it is time to `merge`. You only have to specify a function that takes as many arguments as there are branches. `merge` will flatten and unpack the `PypelyTuple` calculated by a previous `fork` and forward it to the specified function. `merge` returns the output of the specified function. Use `merge` to have a lovily breakfast:


```python
def set_table(tea: 🍵, eggs: 🍳, bread: 🍞, plate: 🍽️):
    ...

morning_routine = pipeline(
    wake_up,
    go_to_kitchen,
    fork(
        make_tea,
        fry_eggs,
        cut_bread,
        get_plate
    ),
    merge(set_table)
)

morning_routine() # -> 😋
```

#### Inputs
`merge` accepts a `Callable` as input. The `Callable` needs to accept as many fields as there are in the given `PypelyTuple` as they will be unpacked and forwarded to the given `Callable`

#### Outputs
`merge` returns a `Callable` that consumes a `PypelyTuple`. The output is as the output of the given `Callable` of type `T`. 

### To

> **Signature** `(obj: T, *set_fields: str) -> Callable[[PypelyTuple], T]` <br>
> **Import** `from pypely import to`

A second way of joining multiple branches is using `to`. This function will forward the output of each branch to a data container. This could e.g. be a `dataclass` or a `namedtuple`. Like `merge`, `to` will also flatten the output of a previous `fork`. You can also define to which field of the given data container an output should be assigned. To do so define the field names as `str`. If no field names are given, the outputs will be applied to the given the container in the order they are created by `fork`:

```python
@dataclass
class Table: 
    tea: Tea
    eggs: Eggs
    bread: Bread
    plate: Plate

morning_routine = pipeline(
    wake_up,
    go_to_kitchen,
    fork(
        make_tea,
        fry_eggs,
        cut_bread,
        get_plate
    ),
    to(Table)
)
```

Imagine a different definition of the `Table` class:

```python
@dataclass
class Table: 
    tea: Tea
    plate: Plate
    bread: Bread
    eggs: Eggs
    size: Optional[int] = None
    color: Optional[str] = None
```

You could change the order of the functions in `fork` to match the order of the fields of `Table`. Another way is to use field names in `to`. Note that you do not need to specify the two `Optional` fields:

```python
morning_routine = pipeline(
    wake_up,
    go_to_kitchen,
    fork(
        make_tea,
        fry_eggs,
        cut_bread,
        get_plate
    ),
    to(Table, "tea", "eggs", "bread", "plate")
)
```

#### Inputs
`to` takes an object of type `T` and an unlimited number of optional `str` as input. The given `str`s describe the name and order of the field names. 

#### Outputs
`to` outputs a `Callable` that consumes a `PypelyTuple` and returns an object of type `T`. The content of thy `PypelyTuple` is assigned to the field names in the order they are given to `to` if they are given or in default order if no field names are specified. 


### Identity

> **Signature** `(x: T) -> T`
> **Import** `from pypely import identity`

The only purpose of this function is to forward the input. This can be used for intermediate results to bypass other steps and make them available in later steps.