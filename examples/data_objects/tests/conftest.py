"""noqa: D100."""
import data_objects.src.morning_routine
from data_objects.src.data import Bread, Eggs, Me, Plate, Table, Tea
from pytest import fixture


@fixture
def sleeping_me() -> Me:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return Me(position="Bed", awake=False, hungry=True)


@fixture
def awake_me() -> Me:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return Me(position="Bed", awake=True, hungry=True)


@fixture
def me_in_kitchen() -> Me:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return Me(position="Kitchen", awake=True, hungry=True)


@fixture
def table() -> Table:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    return Table([Tea(), Eggs(), Bread(), Plate()])


@fixture(autouse=True)
def set_sleep_time_to_zero(mocker):
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    mocker.patch.object(data_objects.src.morning_routine, "TIME_BETWEEN_STEPS", 0)
