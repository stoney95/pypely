from pytest import fixture


@fixture
def add():
    return lambda x, y: x + y


@fixture
def mul():
    return lambda x, y: x * y


@fixture
def sub():
    return lambda x, y: x - y