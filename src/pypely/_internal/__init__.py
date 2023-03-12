"""I provide functionality that `pypely` uses internally.

> **This especially means that my modules are not meant to be used by users directly**

I am the core of `pypely` and will grow with the further development of it. 
The core functionalities are the value providers of this package.

My submodules currently provide these functionalities:
- Dependency detection: The dependencies required by a function are automatically detected. This can be used to create remote environments seamlessly
- Type checking at buildtime: When a pipeline is constructed the compatability of the steps is checked. This provides information about incompatability during buildtime instead of runtime
"""
