from typing import List, Tuple
from pypely import pipeline, merge, fork
from collections import namedtuple


Pipeline = namedtuple('Pipeline', ['funcs', 'name'])
Step = namedtuple('Step', ['func'])
Fork = namedtuple('Fork', ['funcs'])
Merge = namedtuple('Merge', ['func'])


def _is(_type):
    def inner(func):
        is_from_core_modul = func.__module__ == "pypely.core.functions"
        is_type = func.__qualname__.startswith(_type)

        return is_type and is_from_core_modul
    
    return inner

is_pipeline = _is("pipeline")
is_fork = _is("fork")
is_merge = _is("merge")



def add(x,y):
    return x+y

def multiply(x):
    return x * 5

def subtract(x):
    return x - 2

def decompose(pipe):
    if is_pipeline(pipe):
        inside_pipeline = pipe.__closure__[0].cell_contents.__closure__
        last = inside_pipeline[1].cell_contents

        debug_memory = inside_pipeline[0].cell_contents
        firsts = traverse(debug_memory)
        steps = [*firsts, last]
        return Pipeline(funcs=[decompose(step) for step in steps], name=pipe.__name__)
    if is_fork(pipe):
        parallel_steps = pipe.__closure__[0].cell_contents
        return Fork([decompose(step) for step in parallel_steps])
    if is_merge(pipe):
        return Merge(pipe.__closure__[0].cell_contents)
    else:
        return Step(pipe)


def traverse(debug_memory, memory=None):
    if memory is None:
        memory = []

    if debug_memory.combine != debug_memory.first:
        new_debug_memory = debug_memory.combine.__closure__[0].cell_contents
        memory.append(debug_memory.last)
        return traverse(new_debug_memory, memory)
    else:
        memory.append(debug_memory.first)
        return reversed(memory)

    
def print_decomposed(steps, level=0):
    tabs = '\t' * level
    for step in steps:
        if type(step) is Step:
            print(f"{tabs}{step.func.__name__}")
        elif  type(step) is Fork:
            names = ", ".join([s.func.__name__ for s in step.funcs])
            print(f"{tabs}||{names}||")
        elif type(step) is Merge:
            print(f"{tabs}->{step.func.__name__}")
        else:
            print_decomposed(step, level + 1)

second_level = pipeline(subtract, subtract)

inner_pipe = pipeline(
    subtract, subtract, second_level, subtract,
)

test = pipeline(
    add, 
    fork(
        second_level,
        multiply,
    ),
    merge(add),
    inner_pipe, 
    multiply, 
    subtract
)

decomposed_pipe = decompose(test)


def flowchart(steps: list, chart: str=None, edges: List[Tuple[str, str]]=list(), prev_nodes: List[str]=None, i=0, level=1):
    tabs = " " * 2 * level
    if chart is None:
        chart = "flowchart TB" 
        chart += "\nclassDef pipeline fill:#f9f,stroke:#333,stroke-width:4px;"
        chart += "\nclassDef merge fill:black,stroke:grey,stroke-width:4px;"
        chart += "\nclassDef fork fill:gree,stroke:red,stroke-width:4px;"
        chart += "\nsubgraph initialPipeline [ ]"
        chart += "\ndirection TB"

    step = steps.pop(0)
    if type(step) is Step:
        step_name = f"step{i}"
        chart += f"\n{tabs}{step_name}([{step.func.__name__}])"
        if prev_nodes is not None:
            for node in prev_nodes:
                edges.append((node, step_name))
        added_nodes = [step_name]

    elif type(step) is Fork:
        added_nodes = []
        fork_name = f"fork{i}"
        chart += f"\n{tabs}subgraph {fork_name} [fork]"
        for s in step.funcs:
            chart, edges, i = flowchart([s], chart, edges, prev_nodes, i+1, level+1)
            added_nodes.append(f"step{i}")
        chart += f"\n{tabs}end"
        chart += f"\n{tabs}class {fork_name} fork"

    elif type(step) is Merge:
        step_name = f"step{i}"
        chart += f"\n{tabs}subgraph merge{i} [merge]"
        chart += f"\n{tabs}{step_name}([{step.func.__name__}])"
        chart += f"\n{tabs}end"
        chart += f"\n{tabs}class merge{i} merge"
        if prev_nodes is not None:
            for node in prev_nodes:
                edges.append((node, step_name))
        added_nodes = [step_name]

    elif type(step) is Pipeline:
        pipeline_name = f"pipeline{i}"
        chart += f"\n{tabs}subgraph {pipeline_name} [ ]"
        chart, edges, i = flowchart(step.funcs, chart, edges, prev_nodes, i, level+1)
        chart += f"\n{tabs}end"
        chart += f"\nclass {pipeline_name} pipeline"
        added_nodes = [f"step{i}"]

    if len(steps) == 0:
        if level == 1:
            for first, second in edges:
                chart += f"\n{tabs}{first}-->{second}"
            
            chart += f"\n{tabs}end"
            chart += f"\nclass initialPipeline pipeline"

        return chart, edges, i
    else:
        return flowchart(steps, chart, edges, added_nodes, i+1, level)

print(decomposed_pipe)



import webbrowser
from pathlib import Path


chart_string, edges, number_of_steps = flowchart(decomposed_pipe.funcs)
html_string = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
</head>
<body>
  <div class="mermaid">
  {chart_string}
  </div>
 <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
 <script>mermaid.initialize({{startOnLoad:true}});</script>
</body>
</html>
"""

print(edges)
print(number_of_steps)

html_file = Path("mermaid.html").resolve()

with open(html_file, "w") as f:
    f.write(html_string)

new = 2 # open in a new tab, if possible
url = f"file://{html_file}"
webbrowser.open(url,new=new)