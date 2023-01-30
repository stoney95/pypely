from pytest import fixture
from pathlib import Path


@fixture
def add():
    def _add(x: int, y: int) -> int:
        return x + y
    return _add


@fixture
def mul():
    def _mul(x: int, y: int) -> int:
        return x * y
    return _mul


@fixture
def sub():
    def _sub(x: int, y: int) -> int:
        return x - y
    return _sub


@fixture
def root_dir():
    file_dir = Path(__file__).parent.resolve()
    return file_dir.parent.resolve()