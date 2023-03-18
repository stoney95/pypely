**Going from local functions to cloud deployed pipelines in no time :rocket:!** 
`pypely` simplifies and streamlines the definition of pipelines. `pypely` pipelines can be converted into many well known pipeline frameworks.

!!! warning

    `pypely` is work in progress. The [API Reference][reference] shows what is currently usable. Whereas this page also shows the vision of `pypely`.

## Installation
To install `pypely` run: 

```shell
pip install pypely
```

## Important Links
- [API Reference][reference]
- [Contributing][nice-that-you-are-here]
- [Examples](https://github.com/stoney95/pypely/tree/main/examples)

## Why should I use `pypely`?
The pipeline resides at the core of data and machine learning. There are many great libraries that allow you to define and run pipelines in production. So, why another pipeline library? 

Each library has its own way to define a pipeline. `pypely` is here to streamline how pipelines are defined. Streamlining the pipeline definitions brings a lot of benefits:

* No library lock in.
* Start locally, deploy later easily.
* Pipeline basics are automatically covered by `pypely`. To learn more about that check out the [features](#features) section
* Testability of steps is simplified.

## Features
You get the following features with no additional effort when using `pypely`.

### Dependency detection
To run pipelines in a remote environment you need to manage the required dependencies. `pypely` automatically detects the dependecies for each step. This includes packages installed from PyPI as well as dependencies to your local modules. You don't need to worry anymore about the dependencies, `pypely` is doing this for you.

### Compatability checks
Pipelines often run for hours - just to fail in one of the last steps. Often times only because an input did not match the previous output. `pypely` relies on type annotations to check the compatability of each step. The compatability is checked when the pipeline is created. So, errors are catched as early as possible.