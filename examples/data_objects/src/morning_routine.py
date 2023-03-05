"""noqa: D100."""
import time

from data_objects.src import data

from pypely import fork, merge, pipeline
from pypely.memory import memorizable

TIME_BETWEEN_STEPS = 1


def main():
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    morning_routine = pipeline(
        wake_up,
        go_to_kitchen >> "me_in_kitchen",
        fork(make_tea, fry_eggs, cut_bread, get_plate),
        merge("me_in_kitchen" >> set_table),
        "me_in_kitchen" >> have_breakfast,
    )

    sleeping_me = data.Me(position="Bed", awake=False, hungry=True)

    __tab_print("Before morning_routine:", sleeping_me)
    after_morning_routine = morning_routine(sleeping_me)
    __tab_print("After morning_routine:", after_morning_routine)


def wake_up(me: data.Me) -> data.Me:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    new_me = data.Me(position=me.position, awake=True, hungry=me.hungry)
    __tab_print("wake_up:", new_me)
    return new_me


@memorizable
def go_to_kitchen(me: data.Me) -> data.Me:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    new_me = data.Me(position="Kitchen", awake=me.awake, hungry=me.hungry)
    __tab_print("go_to_kitchen:", new_me)
    return new_me


def make_tea(me: data.Me) -> data.Tea:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    __check_me(me)
    tea = data.Tea()
    new_me = data.Me(position=me.position, awake=me.awake, hungry=me.hungry, preparing=tea)
    __tab_print("make_tea:", new_me)

    return tea


def fry_eggs(me: data.Me) -> data.Eggs:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    __check_me(me)
    eggs = data.Eggs()
    new_me = data.Me(position=me.position, awake=me.awake, hungry=me.hungry, preparing=eggs)
    __tab_print("fry_eggs:", new_me)
    return eggs


def cut_bread(me: data.Me) -> data.Bread:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    __check_me(me)
    bread = data.Bread()
    new_me = data.Me(position=me.position, awake=me.awake, hungry=me.hungry, preparing=bread)
    __tab_print("cut_bread:", new_me)
    return bread


def get_plate(me: data.Me) -> data.Plate:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    __check_me(me)
    plate = data.Plate()
    new_me = data.Me(position=me.position, awake=me.awake, hungry=me.hungry, preparing=plate)
    __tab_print("get_plate:", new_me)
    return plate


@memorizable
def set_table(me: data.Me, tea: data.Tea, eggs: data.Eggs, bread: data.Bread, plate: data.Plate) -> data.Table:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    __check_me(me)
    table = data.Table(objects_on_table=[tea, eggs, bread, plate])
    __tab_print("set_table:", f"{me} at {table}")
    return table


@memorizable
def have_breakfast(me: data.Me, table: data.Table) -> data.Me:
    """noqa: D103.

    # noqa: DAR101
    # noqa: DAR201
    """
    __check_me(me)
    if table.is_set:
        return data.Me(position=me.position, awake=me.awake, hungry=False)
    else:
        print(f"{me} at {table}")
        return me


def __check_me(me: data.Me) -> None:
    """noqa: D105.

    # noqa: DAR101
    # noqa: DAR201
    # noqa: DAR401
    """
    if not me.position == "Kitchen":
        raise ValueError(f"You are not in the kitchen: {me}")


def __tab_print(first, second):
    """noqa: D105.

    # noqa: DAR101
    # noqa: DAR201
    """
    all_tabs = 5
    to_remove = len(first) // 8
    num_tabs = all_tabs - to_remove

    tabs = "".join(["\t"] * num_tabs)
    message = f"{first}{tabs}{second}"
    message = message.expandtabs(8)
    print(message)

    time.sleep(TIME_BETWEEN_STEPS)


if __name__ == "__main__":
    main()
