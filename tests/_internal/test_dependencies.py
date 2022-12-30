from pathlib import Path
from typing import Iterable
from dependency_test_modules.module_for_imports import add, process

import pandas as pd
import numpy as np
import requests

from pypely._internal.dependencies import StandardLibDependency, create_environment, identify_dependencies, parse_pip_dependencies, parse_local_dependencies, identify_recursive_dependencies, PipDependency, LocalDependency, DependencyImport, DependencyFromImport, Environment


def test_identify_dependencies_identifies_all_direct_dependencies():
    """I test that all direct dependencies required by the function are identified."""
    # Prepare
    expected_dependencies = [
        DependencyImport(package="json", direct_import=True, alias=None),
        DependencyImport(package="pandas", alias="pd", direct_import=True),
        DependencyImport(package="numpy", alias="np", direct_import=True),
        DependencyFromImport(package="numpy.testing", functionality="assert_array_equal", direct_import=True, alias=None),
    ]

    # Act
    dependencies = identify_dependencies(process)

    # Compare    
    assert_dependencies_match(expected_dependencies, dependencies)


def test_identify_dependencies_identifies_local_dependencies():
    """I test that also local dependencies and relative imports are correctly identified."""
    # Prepare
    expected_dependencies = [
        DependencyFromImport(package="dependency_test_modules.helper_module", functionality="try_request", direct_import=True, alias=None)
    ]

    # Act
    dependencies = identify_dependencies(add)

    # Compare
    assert_dependencies_match(expected_dependencies, dependencies)


def test_identify_recursive_dependencies_identifies_all_imports():
    """I test that all recursive imports are found and correctly resolved."""
    # Prepare
    expected_dependencies = [
        DependencyImport(package="requests", direct_import=False, alias=None),
        DependencyImport(package="json", direct_import=False, alias=None),
        DependencyFromImport(package="dependency_test_modules.yet_another_module", functionality="another_helper", direct_import=False, alias=None),
        DependencyFromImport(package="dependency_test_modules.a.very.nested.package.deep_module", functionality="print_low_level", direct_import=False, alias=None),
        DependencyFromImport(package="dependency_test_modules.a.very.higher_level_module", functionality="print_level", direct_import=False, alias=None),
    ]

    # Act
    dependencies = [
        DependencyFromImport(package="dependency_test_modules.helper_module", functionality="try_request", direct_import=True, alias=None)
    ]
    recursive_dependencies = identify_recursive_dependencies(dependencies)

    # Compare
    assert_dependencies_match(expected_dependencies, recursive_dependencies)


def test_identify_pip_dependencies_resolves_pip_packages_correctly():
    """I test that all packages are identified."""
    # Prepare
    expected_packages = [
        PipDependency(name="pandas", version=pd.__version__, usages=set([DependencyImport(package="pandas", alias="pd", direct_import=False)])),
        PipDependency(name="numpy", version=np.__version__, usages=set([DependencyImport(package="numpy", alias="np", direct_import=False), DependencyFromImport(package="numpy.testing", functionality="assert_array_equal", direct_import=False, alias=None)])),
    ]

    # Act
    dependencies = [
        DependencyImport(package="json", direct_import=False, alias=None),
        DependencyImport(package="pandas", alias="pd", direct_import=False),
        DependencyImport(package="numpy", alias="np", direct_import=False),
        DependencyFromImport(package="numpy.testing", functionality="assert_array_equal", direct_import=False, alias=None),
    ]    

    pip_packages = parse_pip_dependencies(dependencies)

    # Compare
    assert_dependencies_match(expected_packages, pip_packages)


def test_identify_local_dependencies_resolves_local_packages_correctly(root_dir):
    """I test that a dependency of an imported module is also identified.
    """
    # Prepare
    expected_dependencies=[
        LocalDependency(
            path=root_dir / "tests" / "_internal" / "dependency_test_modules" / "helper_module.py", 
            relative_path=Path("dependency_test_modules"), 
            usages=set([DependencyFromImport(package="dependency_test_modules.helper_module", functionality="try_request", direct_import=True, alias=None)]),
        ),
        LocalDependency(
            path=root_dir / "tests" / "_internal" / "dependency_test_modules" / "yet_another_module.py", 
            relative_path=Path("dependency_test_modules"), 
            usages=set([DependencyFromImport(package="dependency_test_modules.yet_another_module", functionality="another_helper", direct_import=False, alias=None)]),
        ),
        LocalDependency(
            path=root_dir / "tests" / "_internal" / "dependency_test_modules" / "a" / "very" / "nested" / "package" / "deep_module.py", 
            relative_path=Path("dependency_test_modules/a/very/nested/package"), 
            usages=set([DependencyFromImport(package="dependency_test_modules.a.very.nested.package.deep_module", functionality="print_low_level", direct_import=False, alias=None)]),
        ),
        LocalDependency(
            path=root_dir / "tests" / "_internal" / "dependency_test_modules"  / "a" / "very" / "higher_level_module.py", 
            relative_path=Path("dependency_test_modules/a/very"), 
            usages=set([DependencyFromImport(package="dependency_test_modules.a.very.higher_level_module", functionality="print_level", direct_import=False, alias=None)]),
        ),
    ]

    # Act
    dependencies = [
        DependencyImport(package="requests", direct_import=False, alias=None),
        DependencyImport(package="json", direct_import=True, alias=None),
        DependencyFromImport(package="dependency_test_modules.helper_module", functionality="try_request", direct_import=True, alias=None),
        DependencyFromImport(package="dependency_test_modules.yet_another_module", functionality="another_helper", direct_import=False, alias=None),
        DependencyFromImport(package="dependency_test_modules.a.very.nested.package.deep_module", functionality="print_low_level", direct_import=False, alias=None),
        DependencyFromImport(package="dependency_test_modules.a.very.higher_level_module", functionality="print_level", direct_import=False, alias=None)
    ]
    local_dependencies = parse_local_dependencies(dependencies)

    # Compare
    assert_dependencies_match(local_dependencies, expected_dependencies)


def test_environment_gets_created_correctly_for_process():
    """I test that the correct environment gets created for the `process` function."""
    # Prepare
    expected = Environment(
        pip_dependencies=set([
            PipDependency(name="pandas", version=pd.__version__, usages=set([DependencyImport(package="pandas", alias="pd", direct_import=True)])),
            PipDependency(name="numpy", version=np.__version__, usages=set([DependencyImport(package="numpy", alias="np", direct_import=True), DependencyFromImport(package="numpy.testing", functionality="assert_array_equal", direct_import=True, alias=None)])),
        ]),
        local_dependencies=set(),
        standard_lib_dependencies=set([
            StandardLibDependency(name="json", usages=set([DependencyImport(package="json", alias=None, direct_import=True)]))
        ])
    )

    # Act
    process_environment = create_environment(process)

    # Compare
    assert process_environment == expected


def test_environment_gets_created_correctly_for_add(root_dir):
    # Prepare
    expected = Environment(
        pip_dependencies=set([
            PipDependency(name="requests", version=requests.__version__, usages=set([DependencyImport(package="requests", direct_import=False, alias=None)])),
        ]),
        local_dependencies=set([
            LocalDependency(
                path=root_dir / "tests" / "_internal" / "dependency_test_modules" / "helper_module.py", 
                relative_path=Path("dependency_test_modules"), 
                usages=set([DependencyFromImport(package="dependency_test_modules.helper_module", functionality="try_request", direct_import=True, alias=None)]),
            ),
            LocalDependency(
                path=root_dir / "tests" / "_internal" / "dependency_test_modules" / "yet_another_module.py", 
                relative_path=Path("dependency_test_modules"), 
                usages=set([DependencyFromImport(package="dependency_test_modules.yet_another_module", functionality="another_helper", direct_import=False, alias=None)]),
            ),
            LocalDependency(
                path=root_dir / "tests" / "_internal" / "dependency_test_modules" / "a" / "very" / "nested" / "package" / "deep_module.py", 
                relative_path=Path("dependency_test_modules/a/very/nested/package"), 
                usages=set([DependencyFromImport(package="dependency_test_modules.a.very.nested.package.deep_module", functionality="print_low_level", direct_import=False, alias=None)]),
            ),
            LocalDependency(
                path=root_dir / "tests" / "_internal" / "dependency_test_modules"  / "a" / "very" / "higher_level_module.py", 
                relative_path=Path("dependency_test_modules/a/very"), 
                usages=set([DependencyFromImport(package="dependency_test_modules.a.very.higher_level_module", functionality="print_level", direct_import=False, alias=None)]),
            ),
        ]),
        standard_lib_dependencies=set([
            StandardLibDependency(name="json", usages=set([DependencyImport(package="json", alias=None, direct_import=False)]))
        ])
    )

    # Act
    add_environment = create_environment(add)

    # Compare
    assert add_environment == expected


def assert_dependencies_match(arr1: Iterable[str], arr2: Iterable[str]) -> None:
    """I assert that the two iterables contain the same elements.

    Args:
        arr1 (Iterable[str]): The first iterable
        arr2 (Iterable[str]): The second iterable
    """
    for dep in arr1:
        assert dep in arr2

    assert len(arr1) == len(arr2)
