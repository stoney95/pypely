# from bs4 import BeautifulSoup
# from pathlib import Path
# from pypely.components import decompose, is_operation, is_fork, is_merge, is_pipeline, is_memorizable, Step
# from typing import Callable, List, Tuple
# from collections import namedtuple
# import tempfile
# import webbrowser
# import time


# HERE = Path(__file__).parent.resolve()
# TEMPLATE_PATH = HERE / "template.html"
# MemoryConnection = namedtuple("MemoryConnection", ["step", "memory_name", "direction"])


# def draw(pipeline: Callable, *, browser: bool=False, path: Path=None, print_info: bool=False) -> None:
#     """I create a flowchart of the pipeline.

#     Args:
#         pipeline (Callable): The pipeline that will be drawn
#         browser (bool, optional): Indicates if the chart should be shown in the browser directly. Defaults to False.
#         path (Path, optional): If given the chart will be stored in that path. Defaults to None.
#         print_info (bool, optional): If provided the function will print the number of steps and edges. Defaults to False.
#     """
#     components = decompose(pipeline)
#     chart, edges, number_of_steps, _ = _flowchart(components.steps)
#     html = _create_html(chart)

#     if print_info:
#         print(f"Found {len(edges)} edges: {edges}")
#         print(f"Found {number_of_steps} steps")

#     if path is not None:
#         _create_and_open(html, path.resolve(), browser)
#     elif browser:
#         with tempfile.TemporaryDirectory() as tmpdir:
#             path = Path(tmpdir) / "pypely.html"
#             _create_and_open(html, path, browser)
#             time.sleep(0.2)


# def _flowchart(
#     steps: List[Step],
#     chart: str=None,
#     edges: List[Tuple[str, str]]=None,
#     memory_connections: List[MemoryConnection]=None,
#     prev_nodes: List[str]=None,
#     consumers: List[int]=None,
#     i=0,
#     level=1,
#     memorizable=False
# ) -> Tuple[str, List[Tuple[str, str]], int, List[int]]:
#     """I create a flow chart of pipeline.

#     This function is only used internally!
#     The input is the result of `pypely.components.decompose`.
#     The function is used recursively. Many arguments are used to
#     store the state of the recursion. Please see the description
#     of the arguments for details.
#     The function will process each step in the list of steps and create the chart step by step.

#     Args:
#         steps (List[Step]): The result of `pypely.components.decompose`
#         chart (str, optional): An intermediate state of the chart definition. Defaults to None.
#         edges (List[Tuple[str, str]], optional): The edges are create after all nodes have been created. This keeps track of all edges. Defaults to None.
#         memory_connections (List[MemoryConnection], optional): The connections to the memory are drawn after all nodes have been created. This keeps track of all conntections to the memory. Defaults to None.
#         prev_nodes (List[str], optional): Is used to create connections to all previous nodes. Defaults to None.
#         consumers (List[int], optional): This keeps track of references to steps that consume memory objects. Defaults to None.
#         i (int, optional): A counter to give each node a unique id. Is also used to reference steps internally. Defaults to 0.
#         level (int, optional): Is used to keep track of sub-pipelines and other wrapped operations. Defaults to 1.
#         memorizable (bool, optional): Indicates if the current step is wrapped by `pypely.memorizable`. Defaults to False.

#     Returns:
#         Tuple[str, List[Tuple[str, str]], int, List[int]]: (
#             The (intermediate) chart,
#             The edges,
#             The index,
#             The consumers
#         )
#     """
#     if edges is None:
#         edges = []

#     if memory_connections is None:
#         memory_connections = []

#     tabs = " " * 2 * level
#     if chart is None:
#         chart = _create_chart_and_class_definitions()

#     step = steps.pop(0)
#     if is_operation(step):
#         step_name = f"step{i}"
#         chart += f"\n{tabs}{step_name}([{_function_name(step.func)}])"
#         chart += f"\n{tabs}class {step_name} operation"
#         if memorizable:
#             chart += "-memory"
#         if prev_nodes is not None:
#             for node in prev_nodes:
#                 edges.append((node, step_name))
#         added_nodes = [step_name]

#         if consumers is None:
#             consumers = [i]

#     elif is_fork(step):
#         added_nodes = []
#         step_name = f"fork{i}"
#         chart += f"\n{tabs}subgraph {step_name} [ ]"

#         for branch in step.branches:
#             chart, edges, i, _consumers = _flowchart([branch], chart, edges, memory_connections, prev_nodes, None, i+1, level+1)
#             if consumers is None:
#                 consumers = _consumers
#             added_nodes.append(f"step{i}")
#         chart += f"\n{tabs}end"
#         chart += f"\n{tabs}class {step_name} fork"
#         if memorizable:
#             chart += "-memory"

#     elif is_merge(step):
#         step_name = f"step{i}"
#         chart += f"\n{tabs}subgraph merge{i} [ ]"
#         chart += f"\n{tabs}{step_name}([{_function_name(step.func)}])"
#         chart += f"\n{tabs}class {step_name} operation"
#         chart += f"\n{tabs}end"
#         chart += f"\n{tabs}class merge{i} merge"
#         if memorizable:
#             chart += "-memory"
#         if prev_nodes is not None:
#             for node in prev_nodes:
#                 edges.append((node, step_name))
#         added_nodes = [step_name]

#         if consumers is None:
#             consumers = [i]

#     elif is_pipeline(step):
#         step_name = f"pipeline{i}"
#         chart += f"\n{tabs}subgraph {step_name} [ ]"
#         chart, edges, i, _consumers = _flowchart(step.steps, chart, edges, memory_connections, prev_nodes, None, i, level+1)
#         chart += f"\n{tabs}end"
#         chart += f"\nclass {step_name} pipeline"
#         if memorizable:
#             chart += "-memory"
#         added_nodes = [f"step{i}"]
#         if consumers is None:
#             consumers = _consumers

#     elif is_memorizable(step):
#         chart, edges, i, consumers = _flowchart([step.func], chart, edges, memory_connections, prev_nodes, None, i, level+1, memorizable=True)
#         added_nodes = [f"step{i}"]
#         if not step.write_attribute is None:
#             memory_connections.append(MemoryConnection(step=f"step{i}", memory_name=step.write_attribute, direction="to_memory"))
#         if not len(step.read_attributes) == 0:
#             for attribute in step.read_attributes:
#                 for consumer in consumers:
#                     memory_connections.append(MemoryConnection(step=f"step{consumer}", memory_name=attribute, direction="from_memory"))

#     if len(steps) == 0:
#         if level == 1:
#             chart = _add_edges(chart, edges)
#             chart += f"\n{tabs}end"
#             chart += f"\nstyle initialPipeline fill:white,stroke-width:0px;"

#             if len(memory_connections) > 0:
#                 chart += _add_memory(memory_connections)

#         return chart, edges, i, consumers
#     else:
#         return _flowchart(steps, chart, edges, memory_connections, added_nodes, consumers, i+1, level)


# def _create_chart_and_class_definitions() -> str:
#     """I create the basics of the chart.

#     This includes the definitions of the chart type and the classes that are used to style the chart.
#     The flowchart is built using mermaid-js. The `flowchart` chart type is used to visualize a pipeline.
#     There are two classes for each component: One to define the style of the class, another one to adjust
#     the style when the class interacts with the memory.

#     Returns:
#         str: The basic definitions of the flowchart
#     """
#     chart = f"flowchart LR"
#     chart += "\nclassDef operation fill:#053C5E,color:white,stroke:#797B84,stroke-width:1px;"
#     chart += "\nclassDef operation-memory fill:#053C5E,color:white,stroke:#f7948d,stroke-width:3px;"
#     chart += "\nclassDef pipeline fill:#a9ffffb3,stroke:grey,stroke-width:1px;"
#     chart += "\nclassDef pipeline-memory fill:#a9ffffb3,stroke:#f7948d,stroke-width:3px;"
#     chart += "\nclassDef fork fill:#90c8f9b3,stroke:grey,stroke-width:1px;"
#     chart += "\nclassDef fork-memory fill:#90c8f9b3,stroke:#f7948d,stroke-width:3px;"
#     chart += "\nclassDef merge fill:#a5ffd6b3,stroke:grey,stroke-width:1px;"
#     chart += "\nclassDef merge-memory fill:#a5ffd6b3,stroke:#f7948d,stroke-width:3px;"
#     chart += "\nsubgraph initialPipeline [ ]"
#     chart += f"\ndirection LR"

#     return chart
# def _function_name(func: Callable) -> str:
#     """I retrieve the name of a function.

#     Args:
#         func (Callable): The function which should be checked

#     Returns:
#         str: The readable name of the function
#     """
#     return func.__name__.strip('<>_').replace('_', ' ')


# def _add_edges(chart: str, edges: List[Tuple[str, str]]) -> str:
#     """I add all collected edges to the chart.

#     Args:
#         chart (str): The intermediate state of the chart
#         edges (List[Tuple[str, str]]): The collected edges between the already drawn nodes.

#     Returns:
#         str: The new state of the chart, including the edges
#     """
#     tabs = " " * 2
#     for first, second in edges:
#         chart += f"\n{tabs}{first}-->{second}"

#     return chart


# def _add_memory(memory_connections: List[MemoryConnection]) -> str:
#     """I add the memory section of the chart.

#     Args:
#         memory_connections (List[MemoryConnection]): A collection of all memory interactions

#     Returns:
#         str: The new state of the chart, including the memory interactions
#     """
#     added_memory_names = {}

#     chart = ""
#     chart += "\nsubgraph memory [ ]"
#     chart += "\ndirection LR"

#     for i, conn in enumerate(memory_connections):
#         if conn.memory_name not in added_memory_names:
#             chart += f"\nmemory{i}[({conn.memory_name})]"
#             added_memory_names[conn.memory_name] = f"memory{i}"
#         if conn.direction == "to_memory":
#             chart += f"\n{conn.step}o-.->{added_memory_names[conn.memory_name]}"
#         elif conn.direction == "from_memory":
#             chart += f"\n{added_memory_names[conn.memory_name]}o-.->{conn.step}"

#     chart += "\nend"
#     chart += f"\nstyle memory fill:#f7948d,stroke-width:0px;"

#     return chart


# def _create_html(chart: str) -> str:
#     """I create an html file that includes the created chart.

#     This function uses the template.html. This template provides
#     a header and a legend explaining the components of the flowchart.
#     A div with the class `mermaid` is used a placeholder. The created
#     chart will become the content of this placeholder.

#     Args:
#         chart (str): The chart created by `_flowchart`

#     Returns:
#         str: The content of the new html file.
#     """
#     with open(TEMPLATE_PATH, 'r') as f:
#         html_string = f.read()

#     template = BeautifulSoup(html_string, 'html.parser')
#     mermaid = template.body.find('div', attrs={'class': 'mermaid'})
#     mermaid.string = chart

#     return str(template)


# def _create_and_open(html: str, path: str=None, browser: bool=False) -> None:
#     """I create an html file and open it in the browser.

#     Args:
#         html (str): The content of the html file.
#         path (str, optional): The path where the file is stored. Defaults to None.
#         browser (bool, optional): Indicates of the file should be opened. Defaults to False.
#     """
#     with open(path, 'w') as f:
#         f.write(html)

#     if browser:
#         _open_file_in_browser(path)


# def _open_file_in_browser(html_file: str) -> None:
#     """I open an HTML file in the browser.

#     Args:
#         html_file (str): The path to the html file
#     """
#     new = 2
#     url = f"file://{html_file}"
#     webbrowser.open(url, new=new)
