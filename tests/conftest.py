from pytest import fixture


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