from pytest import fixture
from data_objects.src.data import *
import data_objects.src.morning_routine

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

@fixture(autouse=True)
def set_sleep_time_to_zero(mocker):
    mocker.patch.object(data_objects.src.morning_routine, "TIME_BETWEEN_STEPS", 0)