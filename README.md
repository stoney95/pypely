# pypely [![Twitter](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fstoney95%2Fpypely)](https://twitter.com/intent/tweet?text=Check+out+pypely:&url=https%3A%2F%2Fgithub.com%2Fstoney95%2Fpypely)

![PyPI](https://img.shields.io/pypi/v/pypely)
[![GitHub release](https://img.shields.io/github/release/stoney95/pypely)](https://github.com/stoney95/pypely/releases)
[![PyPI download month](https://img.shields.io/pypi/dm/pypely)](https://pypi.org/project/pypely/)
[![PyPI download week](https://img.shields.io/pypi/dw/pypely)](https://pypi.org/project/pypely/)
[![Lint Code Base](https://github.com/stoney95/pypely/actions/workflows/release.yaml/badge.svg)](https://github.com/stoney95/pypely/actions/workflows/release.yaml)
[![GitHub stars](https://img.shields.io/github/stars/stoney95/pypely?style=social)](https://github.com/stoney95/pypely/stargazers)
[![GitHub followers](https://img.shields.io/github/followers/stoney95.svg?style=social&label=Follow&maxAge=2592000)](https://github.com/stoney95?tab=followers)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/stoney95/pypely)

[![codecov](https://codecov.io/gh/stoney95/pypely/branch/main/graph/badge.svg?token=7JH2HHJ5CE)](https://codecov.io/gh/stoney95/pypely)

Make your data processing easy - build pipelines in a functional manner. In general this package will not make your code faster or necessarily make you write less code. The purpose of this package is to make you think differently about data processing. 

![](https://media.giphy.com/media/SACoDGYTvVNhZYNb5a/giphy.gif)

You are encouraged to write your data processing step by step - each step being a function. By naming each step with great awareness and chaining them together you will receive a consise and descriptive scheme of the process. This should give you and your colleagues a nice overview on how the process is structured and makes it easy to understand.
 Addtionally you can test every small step easily.

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

## Why functional?
Functional programming is a data driven approach to building software - so let's move data to the center of our thinking when building data processing pipelines. To illustrate the idea a little more two analogies will be used.

### Railway
The railway analogy used by Scott Wlaschin in [this talk](https://youtu.be/Nrp_LZ-XGsY?t=2617) is a good way of looking at functional programming. With `pypely` you can easily build a route from start to finish without caring about the stops in between. :steam_locomotive: 

In this analogy you should translate:
* **railway stop** to **intermediate result**
* **railway** to **tranformative function**

### Git 
`git` branching might be an even easier analogy: 
![](https://raw.githubusercontent.com/stoney95/pypely/main/assets/git_branch.png?raw=true)

Our every day work is managed by `git` and hopefully you don't need to care about special commit hashes etc.. "Shouldn't it be the same for intermediate results in data processing?" :thinking: - "I guess I just care about raw data and processing results". 

In this analogy you should translate:
* **git commit** to **intermediate result**
* **you writing & commiting code** to **tranformative function**

### Cites by smart people (Who use functional programming) 
> "Design is separating into things that can be composed." - Rich Hickey 

## What can I use this for?
This may be the main question that should be answered. This library focuses on structuring data processing, so consider it for dataframes operations. There are two libraries that need to be mentioned:
* [pandas](https://pandas.pydata.org/)
* [pyspark](http://spark.apache.org/docs/latest/api/python/)

But :point_up:.. if you want to build your whole application in a functional style, `pypely` provides you with the basics for this. So get creative 🤩 


# Contribution
If you want to contribute:
1. I'm super happy 🥳
2. Please check out the [contribution guide](https://github.com/stoney95/pypely/tree/main/assets/CONTRIBUTION.md)
3. See the [issues](https://github.com/stoney95/pypely/issues) to find a contribution possibility