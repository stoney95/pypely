from pypely import pipeline, merge, fork
from pypely.visual import draw


def add(x,y):
    return x+y

def multiply(x):
    return x * 5

def subtract(x):
    return x - 2

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
    subtract, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply, 
    multiply,
)


from pathlib import Path

store_here = Path("mermaid.html")
draw(test, path=store_here)

