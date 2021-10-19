import pytest

from morning_routine.src import *
from morning_routine.src.data import *


def test_main():
    main()


def test_wake_up(sleeping_me):
    to_test = wake_up(sleeping_me)

    assert sleeping_me == Me(position="Bed", awake=False, hungry=True)
    assert to_test == Me(position="Bed", awake=True, hungry=True)


def test_go_to_kitchen(awake_me):
    to_test = go_to_kitchen(awake_me)

    assert awake_me == Me(position="Bed", awake=True, hungry=True)
    assert to_test == Me(position="Kitchen", awake=True, hungry=True)


def test_kitchen_activities(me_in_kitchen, awake_me):
    inputs = [
        (make_tea, Tea()),
        (fry_eggs, Eggs()),
        (cut_bread, Bread()),
        (get_plate, Plate())
    ]

    [__test_kitchen_activity(me_in_kitchen, awake_me, func, expected) for func, expected in inputs]


def __test_kitchen_activity(me_in_kitchen, awake_me, func, expected):
    def __test_success():
        to_test = func(me_in_kitchen)
    
        assert __still_in_kitchen(me_in_kitchen)
        assert to_test == expected

    def __test_failure():
        with pytest.raises(ValueError):
            func(awake_me)

    __test_success()
    __test_failure()


def __still_in_kitchen(me):
    return me == Me(position="Kitchen", awake=True, hungry=True)


def test_set_table(me_in_kitchen):
    table = set_table(me_in_kitchen, Tea(), Eggs(), Bread(), Plate())

    assert __still_in_kitchen(me_in_kitchen)
    assert table.is_set
    assert table.objects_on_table == [Tea(), Eggs(), Bread(), Plate()]


def test_have_breakfast(me_in_kitchen, table):
    to_test = have_breakfast(me_in_kitchen, table)

    assert __still_in_kitchen(me_in_kitchen)
    assert to_test == Me(position="Kitchen", awake=True, hungry=False)


def test_have_breakfast_not_in_kitchen(awake_me, table):
    with pytest.raises(ValueError):
        have_breakfast(awake_me, table)


def test_have_breakfast_on_empty_table(me_in_kitchen):
    to_test = have_breakfast(me_in_kitchen, Table())

    assert __still_in_kitchen(me_in_kitchen)
    assert to_test == me_in_kitchen