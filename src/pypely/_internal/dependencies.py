from dataclasses import dataclass
from isort import place_module
import importlib
import importlib_metadata
from pathlib import Path
import sys
from types import ModuleType
from typing import Callable, Dict, Iterable, List, Optional, Set, Union

import pathlib
import pkg_resources

import ast
import inspect

import logging

logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class _Import:
    """I describe a dependency import in general

    Attributes:
        package (str): The imported package.
        alias (str): The used alias.
        direct_import: True if the dependency is imported in the same module as the function.
            If dependency is required directly it needs to be imported to run the function. 
            Otherwise it is a recursive dependency that is imported by one of the direct dependencies. This dependency has not to be imported.
    """
    package: str
    direct_import: bool
    alias: Optional[str]


@dataclass(unsafe_hash=True)
class DependencyImport(_Import):
    """I describe dependency import in the form of import .. (as ..)"""


@dataclass(unsafe_hash=True)
class DependencyFromImport(_Import):
    """I describe dependency import in the form of from .. import .. (as ..)

    Attributes:
        functionality (str): The imported functionality
    """
    functionality: str


@dataclass
class _Dependency:
    """I describe a dependency in general.

    Attributes:
        usages (Set[Union[DependencyImport, DependencyFromImport]]): This describes how the dependency is imported by the function.
    """
    usages: Set[Union[DependencyImport, DependencyFromImport]]

    def __hash__(self) -> int:
        return hash(tuple(self.usages))


@dataclass
class StandardLibDependency(_Dependency):
    """I describe a dependency to a python standard library.

    Attributes:
        name (str): The name of the standard library.
    """
    name: str

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.name))


@dataclass
class PipDependency(_Dependency):
    """I describe a pip dependency.

    Attributes:
        name (str): The name of the pip dependency.
        version (Optional[str]): The version of the pip dependency.
            If the version is `None` it will be installed with the latest version on a remote environment.
    """
    name: str
    version: Optional[str]=None

    def __hash__(self):
        return hash((super().__hash__(), self.name, self.version))


@dataclass
class LocalDependency(_Dependency):
    """I describe a local dependency.

    Attributes:
        path (Path): The path where the module is located.
        relative_path (Path): The destination path of the .py file relative to the import root. 
            This is where the file will be moved to. This ensures that the import statement will work on the remote environment.
    """
    path: Path
    relative_path: Path

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.path, self.relative_path))


@dataclass
class Environment:
    """I describe the environment required to run a function.

    Attributes:
        pip_dependencies (Set[PipDependency]): The collection of required pip dependencies.
        local_dependencies (Set[LocalDependency]): The collection of required local dependencies.
    """
    pip_dependencies: Set[PipDependency]
    local_dependencies: Set[LocalDependency]
    standard_lib_dependencies: Set[StandardLibDependency]


Imports = Union[DependencyFromImport, DependencyImport]


def create_environment(func: Callable) -> Environment:
    """I identify the environment of a given callable.

    This includes a collection of all pip dependencies as well as all local dependencies.

    Args:
        func (Callable): The function for which the dependencies are identified.

    Returns:
        Environment: The environment required to run the function "somewhere else".
    """
    function_dependencies = identify_dependencies(func)
    recursive_dependencies = identify_recursive_dependencies(function_dependencies)
    all_dependencies = function_dependencies.union(recursive_dependencies)

    pip_dependencies = parse_pip_dependencies(all_dependencies)
    local_dependencies = parse_local_dependencies(all_dependencies)
    standard_lib_dependencies = parse_standard_lib_dependencies(all_dependencies)

    return Environment(
        pip_dependencies=pip_dependencies, 
        local_dependencies=local_dependencies,
        standard_lib_dependencies= standard_lib_dependencies    
    )


def identify_dependencies(func: Callable) -> Set[Imports]:
    """I identify all dependencies the given function requires.

    The dependencies can contain pip packages and local modules.

    Args:
        func (Callable): The function for which the dependencies should be identified

    Returns:
        Set[str]: A collection of all required dependencies
    """
    func_module = inspect.getmodule(func)
    dependency_usages = _identify_module_dependency_usages(func_module, module_is_func_module=True)
    function_dependencies = _identify_dependencies_required_by_function(func, dependency_usages)

    return function_dependencies


def _identify_module_dependency_usages(module: ModuleType, module_is_func_module: bool) -> Dict[str, Imports]:
    """I identify all dependencies of the module the func is located in.

    Args:
        func (Callable): The function for which the module dependencies will be searched.
        module_is_func_module (bool): This indicates if the given module is the same as the function module.

    Returns:
        Dict[str, str]: A mapping of used names to the names of the modules they have been imported from.
    """
    source = inspect.getsource(module)
    tree = ast.parse(source)

    dependency_usages = dict()
    for node in ast.walk(tree):
        dependency_usages = _parse_import_statements(node, dependency_usages, module_is_func_module)
        dependency_usages = _parse_from_import_statements(node, dependency_usages, module_is_func_module)
        dependency_usages = _parse_relative_from_import_statements(node, dependency_usages, module, module_is_func_module)
    
    return dependency_usages
            

def _parse_import_statements(node: ast.AST, _dict: Dict[str, Imports], direct_import: bool) -> Dict[str, Imports]:
    """I parse an `import .. (as ..)` statement.

    The name / alias of the imported module is mapped to the name of the module

    Args:
        node (ast.AST): A node in the syntax tree.
        _dict (Dict[str, Imports]): The current collection of modules and usage names.
        direct_import (bool): This bool is set as the `direct_import` attribute of class `_Import`

    Returns:
        Dict[str, Imports]: The adjusted collection of modules and usage names.
    """
    if not isinstance(node, ast.Import):
        return _dict
    
    for name in node.names:
        if not isinstance(name, ast.alias):
            continue

        _import = DependencyImport(package=name.name, alias=name.asname, direct_import=direct_import)
        
        used_name = name.asname
        if used_name is None:
            used_name = name.name

        _dict[used_name] = _import
    
    return _dict


def _parse_from_import_statements(node: ast.AST, _dict: Dict[str, Imports], direct_import: bool) -> Dict[str, Imports]:
    """I parse an `from .. import .. (as ..)` statement.

    The name / alias of the imported module is mapped to the name of the module

    Args:
        node (ast.AST): A node in the syntax tree.
        _dict (Dict[str, Imports]): The current collection of modules and usage names.
        direct_import (bool): This bool is set as the `direct_import` attribute of class `_Import`

    Returns:
        Dict[str, Imports]: The adjusted collection of modules and usage names.
    """
    if not isinstance(node, ast.ImportFrom):
        return _dict

    if node.level > 0:
        return _dict

    package = node.module
    for name in node.names:
        if not isinstance(name, ast.alias):
            continue

        _import = DependencyFromImport(package=package, functionality=name.name, alias=name.asname, direct_import=direct_import)

        if name.asname:
            used_name = name.asname
        else:
            used_name = name.name
        _dict[used_name] = _import

    return _dict


def _parse_relative_from_import_statements(node: ast.AST, _dict: Dict[str, Imports], module: ModuleType, direct_import: bool) -> Dict[str, Imports]:
    """I parse an `from .<module> import .. (as ..)` statement.

    The name / alias of the imported module is mapped to the name of the module.
    Also the relative relationship is resolved.

    Args:
        node (ast.AST): A node in the syntax tree.
        _dict (Dict[str, Imports]): The current collection of modules and usage names.
        module (ModuleType): The module from which the node is imported.
        direct_import (bool): This bool is set as the `direct_import` attribute of class `_Import`

    Returns:
        Dict[str, Imports]: The adjusted collection of modules and usage names.
    """
    if not isinstance(node, ast.ImportFrom):
        return _dict

    if node.level < 1:
        return _dict

    absolute_module = importlib.import_module(f"{'.'*node.level}{node.module}", module.__package__)
    package = absolute_module.__name__
    for name in node.names:
        if not isinstance(name, ast.alias):
            continue

        _import = DependencyFromImport(package=package, functionality=name.name, alias=name.asname, direct_import=direct_import)

        if name.asname:
            used_name = name.asname
        else:
            used_name = name.name
        _dict[used_name] = _import

    return _dict
    

def _identify_dependencies_required_by_function(func: Callable, dependency_usages: Dict[str, Imports]) -> Set[Imports]:
    """I filter the dependencies if they are required for the function or not.

    Only required dependencies will be part of the result.

    Args:
        func (Callable): The function for which the dependencies should be search.
        _dict (Dict[str, Imports]): The mapping of usage names to the originating module.

    Returns:
        Set[Imports]: The collection of modules required by the function
    """
    func_source = inspect.getsource(func)
    func_tree = ast.parse(func_source)

    required_dependencies = set()
    for node in ast.walk(func_tree):
        if not hasattr(node, "id"):
            continue

        if not node.id in dependency_usages.keys():
            continue

        dependency = dependency_usages[node.id]
        required_dependencies.add(dependency)
    
    return required_dependencies


def identify_recursive_dependencies(dependencies: Iterable[Imports]) -> Set[Imports]:
    """I check the imports of local packages.

    This ensures that all required dependencies are identified.

    Args:
        dependencies (Set[Imports]): The first level dependencies of the function.

    Returns:
        Set[Imports]: The collection of all dependencies deeper down the dependency tree.
    """
    identified_dependencies = set()
    for dependency in dependencies:
        root_package = dependency.package.split(".")[0]
        if _is_available_on_pypi(root_package): continue
        if _is_standard_library(root_package): continue

        module = importlib.import_module(dependency.package)
        import_usages = _identify_module_dependency_usages(module, module_is_func_module=False)
        
        this_level_dependencies = set(import_usages.values())
        next_level_dependencies = identify_recursive_dependencies(this_level_dependencies)
        all_dependencies = this_level_dependencies.union(next_level_dependencies)
        identified_dependencies = identified_dependencies.union(all_dependencies)

    return identified_dependencies


def parse_pip_dependencies(dependencies: Iterable[Imports]) -> Set[PipDependency]:
    """I identify all dependencies that are available on PyPI.

    Args:
        dependencies (Iterable[Imports]): All identified dependencies.

    Returns:
        Set[PipDependency]: The collection of dependencies that are available on PyPI.
    """
    pip_packages: Dict[str, PipDependency] = dict()
    for dependency in dependencies:
        root_package = dependency.package.split(".")[0] 
        if _is_standard_library(root_package): continue
        if not _is_available_on_pypi(root_package): continue

        if not root_package in pip_packages:
            _version = _identify_version_of_package(root_package)
            _package = PipDependency(name=root_package, version=_version, usages=set())
            pip_packages[root_package] = _package
        
        pip_packages[root_package].usages.add(dependency)
        
    return set(pip_packages.values())


def parse_standard_lib_dependencies(dependencies: Iterable[Imports]) -> Set[StandardLibDependency]:
    """I identify all dependencies that are available on PyPI.

    Args:
        dependencies (Iterable[Imports]): All identified dependencies.

    Returns:
        Set[StandardLibDependency]: The collection of dependencies that are available on PyPI.
    """
    standard_lib_packages: Dict[str, StandardLibDependency] = dict()
    for dependency in dependencies:
        root_package = dependency.package.split(".")[0] 
        if not _is_standard_library(root_package): continue

        if not root_package in standard_lib_packages:
            _package = StandardLibDependency(name=root_package, usages=set())
            standard_lib_packages[root_package] = _package
        
        standard_lib_packages[root_package].usages.add(dependency)
        
    return set(standard_lib_packages.values())


def _is_available_on_pypi(package_name: str) -> bool:
    """I check if a package is available on PyPI.

    Args:
        module_name (str): The name of the package.

    Returns:
        bool: True if the package is available.
    """
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        pass
    except pkg_resources.extern.packaging.requirements.InvalidRequirement:
        pass
    except ValueError:
        pass
    
    return False


def _is_standard_library(package_name: str) -> bool:
    """I check if a package is a standard python library.

    Args:
        package_name (str): The name of the package.

    Returns:
        bool: True if the package is a standard python library.
    """
    return place_module(package_name) == "STDLIB"


def _identify_version_of_package(package_name: str) -> Optional[str]:
    """I identify the version the package is currently installed with.

    Args:
        package_name (str): The name of the package.

    Returns:
        Optional[str]: The version of the package. Is None if the package is currently not installed.
    """
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        logger.warning(
            f"The package {package_name} is currently not installed. \
            The version cannot be identified. \
            The package will be installed with the latest version in a remote environment."
        )
    except ValueError:
        logger.warning(
            f"You have specified an invalid name: '{package_name}'. No version will be retrieved."
        )


def parse_local_dependencies(dependencies: Iterable[Imports]) -> Set[LocalDependency]:
    """I parse all required information from the local package.

    This enables the usage of the local package on a remote environment.

    Args:
        local_packages (Iterable[Imports]): A collection of local package names.

    Returns:
        Set[LocalDependency]: A collection of parsed information for each local package
    """
    local_packages: Dict[str, LocalDependency] = dict()
    for dependency in dependencies:
        root_package = dependency.package.split(".")[0]
        if _is_available_on_pypi(root_package): continue
        if _is_standard_library(root_package): continue

        if not dependency.package in local_packages:
            module = importlib.import_module(dependency.package)
            _relative_path = _identify_relative_directory_of_package(dependency.package)
            _package = LocalDependency(
                path=Path(module.__file__),
                relative_path=_relative_path,
                usages=set(),
            )

            local_packages[dependency.package] = _package
        
        local_packages[dependency.package].usages.add(dependency)

    return set(local_packages.values())


def _identify_relative_directory_of_package(package_name: str) -> Path:
    """I identify the directory relative to the import root.

    Example: A module is imported as `from the.path.to.the.module import test`.
        The file module.py which contains the function `test` needs to be stored at
        <root>/the/path/to/the. <root> describes the location where the function
        is executed.

    Args:
        package_name (str): The whole package name

    Returns:
        Path: The path where the .py file will be stored
    """
    path = package_name.replace(".", "/")
    return Path(path).parent