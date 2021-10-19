from pytest import fixture
from morning_routine import *

@fixture
def sleeping_me() -> Me:
    return Me(position="Bed", awake=False, hungry=True)


@fixture
def awake_me() -> Me:
    return Me(position="Bed", awake=True, hungry=True)


@fixture
def me_in_kitchen() -> Me:
    return Me(position="Kitchen", awake=True, hungry=True)


@fixture
def table() -> Table:
    return Table([Tea(), Eggs(), Bread(), Plate()])