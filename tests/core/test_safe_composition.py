from typing import TypeVar

import pytest

from pypely._types import PypelyError
from pypely.core._safe_composition import _resolve_type_var_usage, _track_type_var_usage, _wrap_with_error_handling

T = TypeVar("T")
X = TypeVar("X")


def test_resolve_typevar_usage_resolves_type():
    # Prepare
    def test_func(val: T) -> T:
        return val

    _track_type_var_usage(int, T, test_func)

    # Act
    to_test = _resolve_type_var_usage([T], test_func)

    # Compare
    assert to_test == [int]


def test_resolve_typevar_usage_returns_original_type():
    # Prepare
    def test_func(val: T) -> T:
        return val

    _track_type_var_usage(int, X, test_func)

    # Act
    to_test = _resolve_type_var_usage([T], test_func)

    # Compare
    assert to_test == [T]


def test_wrap_with_error_handling_forwards_PypelyError():
    # Prepare
    def failing_function():
        raise PypelyError("Test error")

    wrapped_function = _wrap_with_error_handling(failing_function)

    with pytest.raises(PypelyError):
        wrapped_function()
