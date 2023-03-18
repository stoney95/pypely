# pypely [![Twitter](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fstoney95%2Fpypely)](https://twitter.com/intent/tweet?text=Check+out+pypely:&url=https%3A%2F%2Fgithub.com%2Fstoney95%2Fpypely)

![PyPI](https://img.shields.io/pypi/v/pypely)
[![GitHub release](https://img.shields.io/github/release/stoney95/pypely)](https://github.com/stoney95/pypely/releases)
[![PyPI download month](https://img.shields.io/pypi/dm/pypely)](https://pypi.org/project/pypely/)
[![PyPI download week](https://img.shields.io/pypi/dw/pypely)](https://pypi.org/project/pypely/)
[![Lint Code Base](https://github.com/stoney95/pypely/actions/workflows/release.yaml/badge.svg)](https://github.com/stoney95/pypely/actions/workflows/release.yaml)
[![GitHub stars](https://img.shields.io/github/stars/stoney95/pypely?style=social)](https://github.com/stoney95/pypely/stargazers)
[![GitHub followers](https://img.shields.io/github/followers/stoney95.svg?style=social&label=Follow&maxAge=2592000)](https://github.com/stoney95?tab=followers)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![codecov](https://codecov.io/gh/stoney95/pypely/branch/main/graph/badge.svg?token=7JH2HHJ5CE)](https://codecov.io/gh/stoney95/pypely)

From local functions to cloud deployed pipelines - build pipelines in a functional manner. This package simplifies and streamlines the development of pipelines. You can start locally and deploy the pipelines later using your favorite framework. Further benefits are:

- You don't lock your pipelines into a framework. You can even convert your `pypely` code to the framework of your desire to develop your pipelines further in that framework. 
- The dependencies for each step are detected automatically. So, you don't need to manage the dependencies.
- The compatability of steps is checked during buildtime. Errors are catch as early as possible.
- You keep your pipelines easily testable.

![](https://media.giphy.com/media/SACoDGYTvVNhZYNb5a/giphy.gif)

## Installation
```shell
pip install pypely
```

## Usage
Use `pypely` to chain functions and structure your data processing code in a readable way.

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

If you want to learn more check out the following links.

## Links
- [Documentation](https://stoney95.github.io/pypely/)
- [Examples](https://github.com/stoney95/pypely/tree/main/examples)
- [API Reference](https://stoney95.github.io/pypely/reference/)

# Contributing
If you want to contribute:
1. Woohoo! 🥳
2. Please check out the [contribution guide](https://github.com/stoney95/pypely/tree/main/docs/CONTRIBUTING.md).
3. See the [issues](https://github.com/stoney95/pypely/issues) to find a contribution possibility or create one to tell your plan and start a discussion.