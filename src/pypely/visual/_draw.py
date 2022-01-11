from bs4 import BeautifulSoup
from IPython.core.display import HTML, display
from pathlib import Path
from pypely.components import decompose, Fork, Merge, Operation, Step, Pipeline, Memorizable
from typing import Callable, List, Optional, Tuple
from collections import namedtuple
import tempfile
import webbrowser
import time


HERE = Path(__file__).parent.resolve()
TEMPLATE_PATH = HERE / "template.html"
MemoryConnection = namedtuple("MemoryConnection", ["step", "memory_name", "direction"])


def draw(pipeline: Callable, *, browser: bool=False, inline: bool=False, path: Path=None, print_info: bool=False) -> Optional[HTML]:
    components = decompose(pipeline) 
    chart, edges, number_of_steps, _ = _flowchart(components.steps)
    html = _create_html(chart)

    if print_info:
        print(f"Found {len(edges)} edges: {edges}")
        print(f"Found {number_of_steps} steps")

    if path is not None:
        _create_and_open(html, path.resolve(), browser)
    elif browser:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "pypely.html"
            _create_and_open(html, path, browser)
            time.sleep(0.2)

    if inline:
        display(HTML(html))


def _flowchart(
    steps: List[Step], 
    chart: str=None, 
    edges: List[Tuple[str, str]]=None, 
    memory_connections: List[MemoryConnection]=None, 
    prev_nodes: List[str]=None,
    consumers: List[int]=None,
    i=0, 
    level=1, 
    memorizable=False
):
    if edges is None:
        edges = []

    if memory_connections is None:
        memory_connections = []

    tabs = " " * 2 * level
    if chart is None:
        chart = f"flowchart LR" 
        chart += "\nclassDef operation fill:#053C5E,color:white,stroke:#797B84,stroke-width:1px;"
        chart += "\nclassDef operation-memory fill:#053C5E,color:white,stroke:#f7948d,stroke-width:3px;"
        chart += "\nclassDef pipeline fill:#a9ffffb3,stroke:grey,stroke-width:1px;"
        chart += "\nclassDef pipeline-memory fill:#a9ffffb3,stroke:#f7948d,stroke-width:3px;"
        chart += "\nclassDef fork fill:#90c8f9b3,stroke:grey,stroke-width:1px;"
        chart += "\nclassDef fork-memory fill:#90c8f9b3,stroke:#f7948d,stroke-width:3px;"
        chart += "\nclassDef merge fill:#a5ffd6b3,stroke:grey,stroke-width:1px;"
        chart += "\nclassDef merge-memory fill:#a5ffd6b3,stroke:#f7948d,stroke-width:3px;"
        chart += "\nsubgraph initialPipeline [ ]"
        chart += f"\ndirection LR"

    step = steps.pop(0)
    if type(step) is Operation:
        step_name = f"step{i}"
        chart += f"\n{tabs}{step_name}([{_function_name(step.func)}])"
        chart += f"\n{tabs}class {step_name} operation"
        if memorizable:
            chart += "-memory"
        if prev_nodes is not None:
            for node in prev_nodes:
                edges.append((node, step_name))
        added_nodes = [step_name]

        if consumers is None:
            consumers = [i]

    elif type(step) is Fork:
        added_nodes = []
        step_name = f"fork{i}"
        chart += f"\n{tabs}subgraph {step_name} [ ]"

        build_consumers = False
        if consumers is None:
            consumers = []
            build_consumers = True

        for branch in step.branches:
            chart, edges, i, _consumers = _flowchart([branch], chart, edges, memory_connections, prev_nodes, None, i+1, level+1)
            if build_consumers:
                consumers += _consumers
            added_nodes.append(f"step{i}")
        chart += f"\n{tabs}end"
        chart += f"\n{tabs}class {step_name} fork"
        if memorizable:
            chart += "-memory"

    elif type(step) is Merge:
        step_name = f"step{i}"
        chart += f"\n{tabs}subgraph merge{i} [ ]"
        chart += f"\n{tabs}{step_name}([{_function_name(step.func)}])"
        chart += f"\n{tabs}class {step_name} operation"
        chart += f"\n{tabs}end"
        chart += f"\n{tabs}class merge{i} merge"
        if memorizable:
            chart += "-memory"
        if prev_nodes is not None:
            for node in prev_nodes:
                edges.append((node, step_name))
        added_nodes = [step_name]

        if consumers is None:
            consumers = [i]

    elif type(step) is Pipeline:
        step_name = f"pipeline{i}"
        chart += f"\n{tabs}subgraph {step_name} [ ]"
        chart, edges, i, _consumers = _flowchart(step.steps, chart, edges, memory_connections, prev_nodes, None, i, level+1)
        chart += f"\n{tabs}end"
        chart += f"\nclass {step_name} pipeline"
        if memorizable:
            chart += "-memory"
        added_nodes = [f"step{i}"]
        if consumers is None:
            consumers = _consumers

    elif type(step) is Memorizable:
        chart, edges, i, consumers = _flowchart([step.func], chart, edges, memory_connections, prev_nodes, None, i, level+1, memorizable=True)
        added_nodes = [f"step{i}"]
        if not step.write_attribute is None:
            memory_connections.append(MemoryConnection(step=f"step{i}", memory_name=step.write_attribute, direction="to_memory"))
        if not len(step.read_attributes) == 0:
            for attribute in step.read_attributes:
                for consumer in consumers:
                    memory_connections.append(MemoryConnection(step=f"step{consumer}", memory_name=attribute, direction="from_memory"))

    if len(steps) == 0:
        if level == 1:
            chart = _add_edges(chart, edges)
            chart += f"\n{tabs}end"
            chart += f"\nstyle initialPipeline fill:white,stroke-width:0px;"

            if len(memory_connections) > 0:
                chart += _add_memory(memory_connections)

        return chart, edges, i, consumers
    else:
        return _flowchart(steps, chart, edges, memory_connections, added_nodes, consumers, i+1, level)

    
def _function_name(func):
    return func.__name__.strip('<>_').replace('_', ' ')


def _add_edges(chart: str, edges: List[Tuple[str, str]]) -> str:
    tabs = " " * 2
    for first, second in edges:
        chart += f"\n{tabs}{first}-->{second}"

    return chart


def _add_memory(memory_connections: List[MemoryConnection]):
    added_memory_names = {}

    chart = ""
    chart += "\nsubgraph memory [ ]"
    chart += "\ndirection LR"

    for i, conn in enumerate(memory_connections):
        if conn.memory_name not in added_memory_names:
            chart += f"\nmemory{i}[({conn.memory_name})]"
            added_memory_names[conn.memory_name] = f"memory{i}"
        if conn.direction == "to_memory":
            chart += f"\n{conn.step}o-.->{added_memory_names[conn.memory_name]}"
        elif conn.direction == "from_memory":
            chart += f"\n{added_memory_names[conn.memory_name]}o-.->{conn.step}"

    chart += "\nend"
    chart += f"\nstyle memory fill:#f7948d,stroke-width:0px;"

    return chart


def _create_html(chart: str) -> str:
    with open(TEMPLATE_PATH, 'r') as f:
        html_string = f.read()

    template = BeautifulSoup(html_string, 'html.parser')
    mermaid = template.body.find('div', attrs={'class': 'mermaid'})
    mermaid.string = chart

    return str(template)


def _create_and_open(html: str, path: str=None, browser: bool=False):
    with open(path, 'w') as f:
        f.write(html)
    
    if browser:
        _open_file_in_browser(path)

    
def _open_file_in_browser(html_file: str):
    new = 2
    url = f"file://{html_file}"
    webbrowser.open(url, new=new)