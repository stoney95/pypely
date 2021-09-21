# pypely
Make your data processing easy.

# Structure (?!)
This package enables you to build pipelines for your data processing in a functional manner.

## Why functional?
Functional programming is a data driven approach to building software. The railway analogy used by Scott Wlaschin in [this talk](https://youtu.be/Nrp_LZ-XGsY?t=2617) is a good way of looking at functional programming. With `pypely` you can easily build a route from start to finish without caring about the stops in between. :steam_locomotive:

An even easier analogy might be this: 
![alt text](./assets/git_branch.png?raw=true)
Our every day work is managed by `git` and hopefully you don't need to care about special commit hashes etc.. Shouldn't it be the same for intermediate results in data processing? :thinking:

> "Design is separating into things that can be composed." - Rich Hickey

I guess you can merge every git branch into another and also create a new branch from every other branch - they should be in the same repository. And for merging you may want to think about merge conflicts. But still branches can be composed and each branch itself is composed of commits.

## Examples