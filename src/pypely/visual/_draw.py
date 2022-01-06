from bs4 import BeautifulSoup
from IPython.core.display import HTML, display
from pathlib import Path
from pypely.components import decompose, Fork, Merge, Operation, Step, Pipeline
from typing import Callable, List, Optional, Tuple
import tempfile
import webbrowser
import time


HERE = Path(__file__).parent.resolve()
TEMPLATE_PATH = HERE / "template.html"



def draw(pipeline: Callable, *, browser: bool=False, inline: bool=False, path: Path=None, print_info: bool=False) -> Optional[HTML]:
    components = decompose(pipeline) 
    chart, edges, number_of_steps = _flowchart(components.steps)
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


def _flowchart(steps: List[Step], chart: str=None, edges: List[Tuple[str, str]]=None, prev_nodes: List[str]=None, i=0, level=1):
    if edges is None:
        edges = []

    tabs = " " * 2 * level
    if chart is None:
        chart = f"flowchart LR" 
        chart += "\nclassDef operation fill:#053C5E,color:white,stroke:#797B84,stroke-width:1px;"
        chart += "\nclassDef pipeline fill:#a9ffffb3,stroke:grey,stroke-width:1px;"
        chart += "\nclassDef fork fill:#90c8f9b3,stroke:grey,stroke-width:1px;"
        chart += "\nclassDef merge fill:#a5ffd6b3,stroke:grey,stroke-width:1px;"
        chart += "\nsubgraph initialPipeline [ ]"
        chart += f"\ndirection LR"

    step = steps.pop(0)
    if type(step) is Operation:
        step_name = f"step{i}"
        chart += f"\n{tabs}{step_name}([{_function_name(step.func)}])"
        chart += f"\n{tabs}class {step_name} operation"
        if prev_nodes is not None:
            for node in prev_nodes:
                edges.append((node, step_name))
        added_nodes = [step_name]

    elif type(step) is Fork:
        added_nodes = []
        fork_name = f"fork{i}"
        chart += f"\n{tabs}subgraph {fork_name} [ ]"
        for branch in step.branches:
            chart, edges, i = _flowchart([branch], chart, edges, prev_nodes, i+1, level+1)
            added_nodes.append(f"step{i}")
        chart += f"\n{tabs}end"
        chart += f"\n{tabs}class {fork_name} fork"

    elif type(step) is Merge:
        step_name = f"step{i}"
        chart += f"\n{tabs}subgraph merge{i} [ ]"
        chart += f"\n{tabs}{step_name}([{_function_name(step.func)}])"
        chart += f"\n{tabs}class {step_name} operation"
        chart += f"\n{tabs}end"
        chart += f"\n{tabs}class merge{i} merge"
        if prev_nodes is not None:
            for node in prev_nodes:
                edges.append((node, step_name))
        added_nodes = [step_name]

    elif type(step) is Pipeline:
        pipeline_name = f"pipeline{i}"
        chart += f"\n{tabs}subgraph {pipeline_name} [ ]"
        chart, edges, i = _flowchart(step.steps, chart, edges, prev_nodes, i, level+1)
        chart += f"\n{tabs}end"
        chart += f"\nclass {pipeline_name} pipeline"
        added_nodes = [f"step{i}"]

    if len(steps) == 0:
        if level == 1:
            chart = _add_edges(chart, edges)
            chart += f"\n{tabs}end"
            chart += f"\nstyle initialPipeline fill:white,stroke-width:0px;"

        return chart, edges, i
    else:
        return _flowchart(steps, chart, edges, added_nodes, i+1, level)

    
def _function_name(func):
    return func.__name__.strip('<>_').replace('_', ' ')


def _add_edges(chart: str, edges: List[Tuple[str, str]]) -> str:
    tabs = " " * 2
    for first, second in edges:
        chart += f"\n{tabs}{first}-->{second}"

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