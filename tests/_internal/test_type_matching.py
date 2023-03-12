from typing import Dict, Iterable, List, NewType, TypeVar, Union

from pypely._internal.type_matching import _do_types_match, _does_resolve_typevar, _get_base_type, is_subtype


def test_is_subtype():
    # Prepare
    class Parent:
        pass

    class Child(Parent):
        pass

    class GrandChild(Child):
        pass

    test_cases = [
        (List[int], Iterable, True),
        (int, Union[int, str], True),
        (str, Union[int, str], True),
        (float, Union[int, str], False),
        (int, Union[float, str], False),
        (TypeVar("T", bound=Union[int, str]), Union[int, str], True),
        (TypeVar("t"), Union[int, str], True),
        (int, float, True),
        (int, TypeVar("test", bound=str), False),
        (int, TypeVar("test", bound=int), True),
        (int, TypeVar("test"), True),
        (List[int], List[str], False),
        (Dict[str, List[int]], Dict[str, List[str]], False),
        (Dict[str, List[int]], Dict[str, List[int]], True),
        (Dict[str, List[int]], Dict[str, Iterable], True),
        (Dict[str, List[int]], Iterable, True),
        (Dict, Iterable, True),
        (Parent, Parent, True),
        (Child, Parent, True),
        (Parent, Child, False),
        (GrandChild, Child, True),
        (GrandChild, Parent, True),
        (GrandChild, GrandChild, True),
        (Child, GrandChild, False),
    ]

    # Act
    # Compare
    for t1, t2, expected in test_cases:
        assert is_subtype(t1, t2) == expected


def test_do_types_match_does_not_fail():
    # Prepare
    class Test:
        pass

    test = Test()

    # Act
    to_test = _do_types_match(int, test)

    # Compare
    assert to_test == False


def test_does_resolve_typevar_works_with_constraints():
    # Prepare
    T = TypeVar("T", str, int)

    # Act
    int_resolves_T = _does_resolve_typevar(int, T)
    str_resolves_T = _does_resolve_typevar(str, T)
    list_resolves_T = _does_resolve_typevar(list, T)

    # Compare
    assert int_resolves_T
    assert str_resolves_T
    assert not list_resolves_T


def test_does_resolve_typevar_works_with_non_typevar_input():
    to_test = _does_resolve_typevar(int, str)
    assert not to_test


def test_get_base_type():
    # Prepare
    T = TypeVar("T")
    TestType = NewType("test_type", int)

    class MyDict(dict[str, T]):
        pass

    # Act
    base_type_new_type = _get_base_type(TestType)
    base_type_generic = _get_base_type(MyDict)

    # Compare
    assert base_type_new_type == int
    assert base_type_generic == MyDict
