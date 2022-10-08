import inspect
import tempfile
import time
from pypely.components import decompose, Step, Merge, Operation, Pipeline, Fork, Memorizable
from typing import Callable, List, Optional, Tuple, Union
from pathlib import Path
from pyvis.network import Network


Previous = Union[Operation, List[Operation]]


def draw(pipeline: Callable, *, show: bool=False, inline: bool=False, path: Path=None) -> None:
    components = decompose(pipeline)
    net = Network(width="100%", height="95%", notebook=inline)
    net, _ = draw_pipeline(net, components.steps)

    net.set_options(
"""var options = {
  "nodes": {
    "fixed": {
      "x": true,
      "y": true
    }
  },
  "edges": {
    "arrows": {
      "to": {
        "enabled": true,
        "scaleFactor": 0.45
      }
    },
    "arrowStrikethrough": true,
    "color": {
      "inherit": true
    },
    "smooth": {
      "type": "cubicBezier",
      "forceDirection": "horizontal",
      "roundness": 0.65
    }
  },
  "interaction": {
    "dragNodes": false,
    "hover": true,
    "navigationButtons": true,
    "zoomView": false
  },
  "physics": {
    "enabled": false,
    "minVelocity": 0.75
  }
}"""
    )

    _save = path is not None
    save_and_show = _save and show
    save_and_dont_show = _save and not show
    just_show = not _save and show
    

    path = str(path.resolve())
    if save_and_show:
        net.show(path)
    if save_and_dont_show:
        net.save_graph(path)
    if just_show:
        with tempfile.TemporaryFile() as f:
            net.show(f)
            time.sleep(0.1)
    

def draw_pipeline(net: Network, steps: List[Step], previous: Optional[Step]=None) -> Tuple[Network, Previous]:
    for step in steps:
        net, previous = draw_step(net, step, previous)

    return net, previous


def draw_step(net: Network, step: Step, previous: Optional[Step]=None) -> Tuple[Network, Previous]:
    if isinstance(step, Operation):
        return draw_operation(net, step, previous)
    if isinstance(step, Fork):
        return draw_fork(net, step, previous)
    if isinstance(step, Merge):
        return draw_merge(net, step, previous)
    if isinstance(step, Memorizable):
        return draw_memorizable(net, step, previous, inputs=step.read_attributes, output=step.write_attribute)
    if isinstance(step, Pipeline):
        return draw_pipeline(net, step.steps, previous)
    
    return net


def draw_operation(net: Network, operation: Operation, previous: Optional[Operation]) -> Tuple[Network, Operation]:
    net = _add_step(net, operation)
    net = _add_edge(net, operation, previous)

    return net, operation


def draw_fork(net: Network, fork: Fork, previous: Optional[Operation]) -> Tuple[Network, List[Operation]]:
    previous_ = []
    for branch in fork.branches:
        net, prev_operation = draw_step(net, branch, previous)
        previous_.append(prev_operation)

    return net, previous_


def draw_merge(net: Network, merge: Merge, previous: List[Operation]) -> Network:
    net = _add_step(net, merge)
    for branch in previous:
        net = _add_edge(net, merge, branch)
    
    return net, merge


def draw_memorizable(net: Network, memorizable: Memorizable, previous: Previous, inputs: List[str], output: str) -> Tuple[Network, Operation]:
    net, prev_operation = draw_step(net, memorizable.func, previous)

    for input in inputs:
        net.add_edge(input, str(prev_operation.id)) # TODO: In case it is a pipeline there should be something like first operation

    net = _add_memory(net, prev_operation, output)
    return net, prev_operation


def _add_step(net: Network, step: Operation) -> Network:
    func = step.func
    name = _function_name(func)
    source = _function_definition(func)
    
    net.add_node(str(step.id), label=name, shape="box", title=source, x=0)
    return net


def _add_memory(net: Network, operation: Operation, output: str) -> Network:
    if not output: return net

    net.add_node(output, label=output, shape="database", x=-100)
    net.add_edge(str(operation.id), output)
    return net


def _add_edge(net: Network, current: Operation, previous: Optional[Operation]=None) -> Network:
    if previous is None: return net
    net.add_edge(str(previous.id), str(current.id))
    
    return net


def _function_name(func):
    return func.__name__.strip('<>_')


def _function_definition(func: Callable) -> str:
    origin = f"Defined in file \"{func.__code__.co_filename}\", line {func.__code__.co_firstlineno}"
    source = inspect.getsource(func).replace("\n", "<br>").replace("    ", "&emsp;")
    source = f"<b>{source}</b>"
    return f"{origin}:<br>{source}"
