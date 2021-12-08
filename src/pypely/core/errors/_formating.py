import inspect
from collections import defaultdict


def format_args(func):
    argspec = inspect.getfullargspec(func)
    annotations = defaultdict(lambda: None)
    for k, v in argspec.annotations.items():
        annotations[k] = v

    def _annotate(annotation):
        if annotation is None:
            return ""
        return f": {annotation}"

    args = ', '.join([f'{x}{_annotate(annotations[x])}' for x in argspec.args])
    return f'({args})'


def func_details(func):
    return f"'{func.__name__}' from File \"{func.__code__.co_filename}\", line {func.__code__.co_firstlineno}"

