from typing import Dict, Iterable, List, TypeVar, Union

from pypely._internal.type_matching import is_subtype


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
