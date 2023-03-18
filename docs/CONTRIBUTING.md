# Nice that you are here!
We are very glad that you are interested in contributing to this project. Please follow this guide as there are some rules. 

## Contributing

Again, we're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

Please note that this project is released with a [Contributor Code of Conduct](https://github.com/stoney95/pypely/tree/main/CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## Issues and PRs

If you have suggestions for how this project could be improved, or want to report a bug, open an issue! We'd love all and any contributions. If you have questions, too, we'd love to hear them.

We'd also love PRs. If you're thinking of a large PR, we advise opening up an issue first to talk about it, though! Look at the links below if you're not sure how to open a PR.

## Submitting a pull request

1. Fork and clone the repository.
1. Configure and install the dependencies: `conda env create -f conda.yaml`.
1. Install the pre-commit hooks: `pre-commit install`. These hooks will format your code, check the typing and ensure that conventional commits are used.
2. Make sure the tests pass on your machine: `source .path && pytest tests examples` (If you work on Windows it is recommended to use the Linux Sub System. Otherwise you can set the PYTHONPATH manually or use [dot sourcing](https://superuser.com/questions/71446/equivalent-of-bashs-source-command-in-powershell))
3. Create a new branch: `git checkout -b my-branch-name`.
4. Make your change, add tests, and make sure the tests still pass.
5. Push to your fork and [submit a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).
6. Pat your self on the back and wait for your pull request to be reviewed and merged.

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

- Use [Conventional Commits](#conventional-commits)
- Write and update tests.
- Keep your changes as focused as possible. If there are multiple changes you would like to make that are not dependent upon each other, consider submitting them as separate pull requests.
- Write a [good commit message](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).

Work in Progress pull requests are also welcome to get feedback early on, or if there is something blocked you.

## Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
- [GitHub Help](https://help.github.com)


## Conventional Commits

> :warning: Be sure to read this section. A bot is installed that will deny your pull request if there are no commits in the format of Conventional Commit.

The project uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to automatically detect project versions. Please read the linked guide to understand [Conventional Commits (CC)](https://www.conventionalcommits.org/en/v1.0.0/). To ensure that you use conventional commits, install the pre-configured pre-commit hooks. One hook will check that you use conventional commits.
