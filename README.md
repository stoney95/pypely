# pypely
Make your data processing easy - build pipelines in a functional manner. In general this package will not make your code faster or necessarily make you write less code. The purpose of this package is to make you think differently about data processing. 

![](https://media.giphy.com/media/SACoDGYTvVNhZYNb5a/giphy.gif)

You are encouraged to write your data processing step by step - each step being a function. By naming each step with great awareness and chaining them together you will receive a consise and descriptive scheme of the process. This should give you and your colleagues a nice overview on how the process is structured and makes it easy to understand.
 Addtionally you can test every small step easily.

## Installation
```shell
pip install pypely
```

## Why functional?
Functional programming is a data driven approach to building software - so let's move data to the center of our thinking when building data processing pipelines. To ilustrate the idea a little more two analogies will be used

### Railway
The railway analogy used by Scott Wlaschin in [this talk](https://youtu.be/Nrp_LZ-XGsY?t=2617) is a good way of looking at functional programming. With `pypely` you can easily build a route from start to finish without caring about the stops in between. :steam_locomotive: 

In this analogy you should translate:
* **railway stop** to **intermediate result**
* **railway** to **tranformative function**

### Git 
`git` branching might be an even easier analogy: 
![alt text](./assets/git_branch.png?raw=true)

Our every day work is managed by `git` and hopefully you don't need to care about special commit hashes etc.. "Shouldn't it be the same for intermediate results in data processing?" :thinking: - "I guess I just care about raw data and processing results". 

In this analogy you should translate:
* **git commit** to **intermediate result**
* **you writing & commiting code** to **tranformative function**

### Cites by smart people (Who use functional programming) 
> "Design is separating into things that can be composed." - Rich Hickey 

## What can I use this for?
So this may be the main question that should be answered. This library focuses on structuring data processing, so consider it for dataframes operations. There are two libraries that need to be mentioned:
* pandas
* pyspark

But :point_up:.. if you want to build your whole application in a functional style, `pypely` provides you with the basics for this. So get creative 🤩 

## Examples
If you want to get inspired or want to see `pypely` in action please check out the [expamples](https://github.com/stoney95/pype/tree/main/src/examples) directory.

# Documentation
The package consists of these functions:
* `pipeline`
* `fork`
* `merge`
* `identity`

and a `helpers` module which provides useful helper functions. Take a look at them an be inspired to write your own - with a perfect fit on your demand. For documentation of the `helpers` module please refer to the [tests]((https://github.com/stoney95/pype/tree/main/tests/test_helpers.py)

In the following the functions will be described and some example code is given. Please also refer to the [tests](https://github.com/stoney95/pype/tree/main/tests/test_functions.py) for a better understaning of each function.

## Identity
Let's start with the simplest one first. The only purpose of this function is to forward the input. This can be used for intermediate results to bypass other steps and make them available in later steps.

## Pipeline
This is the core of the package. `pipeline` allows you to chain defined functions together. The output of a function will be passed as the input to the following function. `pipeline` can be used like the following:

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

## Fork
Sometimes you want to do multiple things with one intermediate result. `fork` allows you to do this. You can specify multiple functions inside `fork`. Each will receive the output of the previous function as the input. `fork` outputs a list with the result of each specified function in the order of the functions. You can use fork like this.

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

morning_routine() # -> [🍵, 🍳, 🍞, 🍽️]
```

## Merge
After you split your process into multiple branches, it is time to `merge`. You only have to specify a function that takes as many arguments as there are branches. `merge` will flatten and unpack the list calculated by a previous `fork` and forward it to the specified function. `merge` return the output of the specified function. Use `merge` to have a lovily breakfast:


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