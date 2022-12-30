from typing import Iterable
from dependency_test_modules.module_for_imports import add, process

from pypely._internal.dependencies import identify_dependencies

def test_identify_dependencies():
    """I test that all packages are identified."""
    # Prepare
    expected_dependencies = ["pandas", "numpy"]

    # Act
    dependencies = identify_dependencies(process)

    # Compare    
    assert_dependencies_match(expected_dependencies, dependencies)


def test_identify_dependencies_identifies_recursive_import():
    """I test that a dependency of an import module is also identified.
    """
    # Prepare
    expected_dependencies = [
        "requests", 
        "json", 
        "dependency_test_modules.helper_module", 
        "dependency_test_modules.yet_another_module", 
        "dependency_test_modules.a.very.nested.package.deep_module",
        "dependency_test_modules.a.very.higher_level_module"
    ]

    # Act
    dependencies = identify_dependencies(add)

    # Compare
    assert_dependencies_match(expected_dependencies, dependencies)


def assert_dependencies_match(arr1: Iterable[str], arr2: Iterable[str]) -> None:
    """I assert that the two iterables contain the same elements.

    Args:
        arr1 (Iterable[str]): The first iterable
        arr2 (Iterable[str]): The second iterable
    """
    for dep in arr1:
        assert dep in arr2

    assert len(arr1) == len(arr2)
