# pypely
Make your data processing easy - build pipelines in a functional manner. In general this package will not make your code faster or necessarily make you write less code. The purpose of this package is to make you think differently about data processing. 

![](https://media.giphy.com/media/SACoDGYTvVNhZYNb5a/giphy.gif)

You are encouraged to write your data processing step by step - each step being a function. By naming each step with great awareness and chaining them together you will receive a consise and descriptive scheme of the process. This should give you and your colleagues a nice overview on how the process i structured and makes it easy to understand.
 Addtionally you can test every small step easily.

## Why functional?
Functional programming is a data driven approach to building software. The railway analogy used by Scott Wlaschin in [this talk](https://youtu.be/Nrp_LZ-XGsY?t=2617) is a good way of looking at functional programming. With `pypely` you can easily build a route from start to finish without caring about the stops in between. :steam_locomotive:

`git` branching might be an even easier analogy: 
![alt text](./assets/git_branch.png?raw=true)
Our every day work is managed by `git` and hopefully you don't need to care about special commit hashes etc.. "Shouldn't it be the same for intermediate results in data processing?" :thinking: - "I guess I just care about raw data and processing results". 

### Cites by smart people (Who use functional programming) 
> "Design is separating into things that can be composed." - Rich Hickey

## Examples
To see `pypely` in action please check out the [expamples](./src/examples) directory.

# Documentation
The package consists of four functions:
* `pipeline`
* `fork`
* `merge`
* `identity`

## Identity
Let's start with the simplest one first. The only purpose of this function is to forward the input. This can be used for intermediate results to bypass other steps. This makes them available in later steps.

## Pipeline
This is the core of the package. `pipeline` allows you to chain defined functions together. The output of a function will be passed as the input to the following function. `pipeline` can be used like the following:

```python
pipe = pipeline(
    open_favourite_ide,
    create_new_conda_environment,
    activate_environment,
    install_pypely,
    have_fun_building_pipelines 
)

pipe() # -> 🥳
```