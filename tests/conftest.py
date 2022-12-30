from pytest import fixture
from pathlib import Path


@fixture
def add():
    def _add(x: int, y) -> int:
        return x + y
    return _add


@fixture
def mul():
    return lambda x, y: x * y


@fixture
def sub():
    return lambda x, y: x - y


@fixture
def root_dir():
    file_dir = Path(__file__).parent.resolve()
    return file_dir.parent.resolve()