# Examples
In this directory are some examples that will showcase how to apply `pypely`. To show different use cases `pypely` can be applied to there are three different types of examples:

* [data_objects](./data_objects/): This example is the implementation of the documentation code snippets. It showcases how `pypely` can be used in combination with custom created immutable data objects.
* **[preprocessing](.preprocessing/)**: This example applies the `pypely` approach to different kaggle data preprocessing examples. **These examples represent the majority of use cases `pypely` can be applied to.**
* [mnist_training](./mnist_training/): The example is referencing [Arjan Codes YouTube tutorials](https://youtu.be/ka70COItN40), where he takes the codebase of a data science project and refactors it. The project trains a simple torch model on mnist data. The example here provides an alternative implementation using `pypely`. 

> :point_up: The order of the list above also demonstrates the complexity of the examples. Where [data_objects](./data_objects/) is a simple example with no real world application, [mnist_training](./mnist_training/) is a small data science project on its own. 

> :mailbox: If you find the approaches in the examples interesting and have feedback, criticisms or questions please feel free to open an issue or contact me directly. 

> :warning: If you want to execute the examples please run `source .path` as this will set the correct `PYTHONPATH`. You can also run the command from any subdirectory as long as you update the path to [.path](../.path) respectively. 

