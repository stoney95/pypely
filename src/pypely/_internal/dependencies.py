from dataclasses import dataclass
from isort import place_module
import importlib

from importlib.util import find_spec
from pathlib import Path
import sys
from types import ModuleType
from typing import Callable, Dict, Iterable, Set

import pkg_resources

import ast
import inspect


@dataclass
class LocalPackage:
    """I describe a local package

    Attributes:
        file_path (Path): The path where the module is located.
        sub_folder_path (Path): The sub-folders relative to the import root. 
            This is where the file will be moved to. This ensures that the import statement will work on the remote environment.
        name (str): The name of the module.
    """
    file_path: Path
    sub_folder_path: Path
    name: str


def identify_dependencies(func: Callable) -> Set[str]:
    """I identify all dependencies the given function requires.

    The dependencies can contain pip packages and local modules.

    Args:
        func (Callable): The function for which the dependencies should be identified

    Returns:
        Set[str]: A collection of all required dependencies
    """
    func_module = inspect.getmodule(func)
    dependency_usages = _identify_module_dependency_usages(func_module)
    function_dependencies = _identify_dependencies_required_by_function(func, dependency_usages)

    recursive_dependencies = _identify_recursive_dependencies(function_dependencies)

    return function_dependencies.union(recursive_dependencies)


def _identify_module_dependency_usages(module: ModuleType) -> Dict[str, str]:
    """I identify all dependencies of the module the func is located in.

    Args:
        func (Callable): The function for which the module dependencies will be searched.

    Returns:
        Dict[str, str]: A mapping of used names to the names of the modules they have been imported from.
    """
    source = inspect.getsource(module)
    tree = ast.parse(source)

    usage_origins = dict()
    for node in ast.walk(tree):
        usage_origins = _parse_import_statements(node, usage_origins)
        usage_origins = _parse_from_import_statements(node, usage_origins)
        usage_origins = _parse_relative_from_import_statements(node, usage_origins, module)
    
    return usage_origins
            

def _parse_import_statements(node: ast.AST, _dict: Dict[str, str]) -> Dict[str, str]:
    """I parse an `import ...` statement.

    The name / alias of the imported module is mapped to the name of the module

    Args:
        node (ast.AST): A node in the syntax tree.
        _dict (Dict[str, str]): The current collection of modules and usage names.

    Returns:
        Dict[str, str]: The adjusted collection of modules and usage names.
    """
    if not isinstance(node, ast.Import):
        return _dict
    
    for name in node.names:
        if not isinstance(name, ast.alias):
            continue

        used_name = name.asname
        if used_name is None:
            used_name = name.name
        _dict[used_name] = name.name
    
    return _dict


def _parse_from_import_statements(node: ast.AST, _dict: Dict[str, str]) -> Dict[str, str]:
    """I parse an `from ... import ...` statement.

    The name / alias of the imported module is mapped to the name of the module

    Args:
        node (ast.AST): A node in the syntax tree.
        _dict (Dict[str, str]): The current collection of modules and usage names.

    Returns:
        Dict[str, str]: The adjusted collection of modules and usage names.
    """
    if not isinstance(node, ast.ImportFrom):
        return _dict

    if node.level > 0:
        return _dict

    root_module = node.module.split('.')[0]
    for name in node.names:
        if not isinstance(name, ast.alias):
            continue

        if name.asname:
            used_name = name.asname
        else:
            used_name = name.name
        _dict[used_name] = root_module

    return _dict


def _parse_relative_from_import_statements(node: ast.AST, _dict: Dict[str, str], module: ModuleType) -> Dict[str, str]:
    """I parse an `from .<module> import ...` statement.

    The name / alias of the imported module is mapped to the name of the module.
    Also the relative relationship is resolved.

    Args:
        node (ast.AST): A node in the syntax tree.
        _dict (Dict[str, str]): The current collection of modules and usage names.
        module (ModuleType): The module from which the node is imported.

    Returns:
        Dict[str, str]: The adjusted collection of modules and usage names.
    """
    if not isinstance(node, ast.ImportFrom):
        return _dict

    if node.level < 1:
        return _dict

    absolute_module = importlib.import_module(f"{'.'*node.level}{node.module}", module.__package__)
    root_module = absolute_module.__name__
    for name in node.names:
        if not isinstance(name, ast.alias):
            continue

        if name.asname:
            used_name = name.asname
        else:
            used_name = name.name
        _dict[used_name] = root_module

    return _dict
    

def _identify_dependencies_required_by_function(func: Callable, usage_origins: Dict[str, str]) -> Set[str]:
    """I filter the dependencies if they are required for the function or not.

    Only required dependencies will be part of the result.

    Args:
        func (Callable): The function for which the dependencies should be search.
        _dict (Dict[str, str]): The mapping of usage names to the originating module.

    Returns:
        Set[str]: The collection of modules required by the function
    """
    func_source = inspect.getsource(func)
    func_tree = ast.parse(func_source)

    required_modules = set()
    for node in ast.walk(func_tree):
        if not hasattr(node, "id"):
            continue

        if not node.id in usage_origins.keys():
            continue

        origin_module = usage_origins[node.id]
        required_modules.add(origin_module)
    
    return required_modules


def _identify_recursive_dependencies(dependencies: Iterable[str]) -> Set[str]:
    """I check the imports of local packages.

    This ensures that all required dependencies are identified.

    Args:
        dependencies (Set[str]): The first level dependencies of the function.

    Returns:
        Set[str]: The collection of all dependencies deeper down the dependency tree.
    """
    pip_packages = identify_pip_packages(dependencies)
    builtin_packages = identify_standard_library_packages(dependencies)
    local_packages = set(dependencies).difference(pip_packages).difference(builtin_packages)

    if len(local_packages) == 0:
        return pip_packages

    identified_dependencies = set()
    for module_name in local_packages:
        module = importlib.import_module(module_name)
        import_usages = _identify_module_dependency_usages(module)
        
        this_level_dependencies = set(import_usages.values())
        next_level_dependencies = _identify_recursive_dependencies(this_level_dependencies)
        all_dependencies = this_level_dependencies.union(next_level_dependencies)
        identified_dependencies = identified_dependencies.union(all_dependencies)

    return identified_dependencies



def identify_standard_library_packages(dependencies: Iterable[str]) -> Set[str]:
    """I identify all dependencies that are python builtins.

    Args:
        dependencies (Iterable[str]): All identified dependencies.

    Returns:
        Set[str]: The collection of dependencies that are python builtins.
    """
    standard_library_packages = set()
    for module_name in dependencies:
        if place_module(module_name) == "STDLIB":
            standard_library_packages.add(module_name)
    
    return standard_library_packages



def identify_pip_packages(dependencies: Iterable[str]) -> Set[str]:
    """I identify all dependencies that are available on PyPI.

    Args:
        dependencies (Iterable[str]): All identified dependencies.

    Returns:
        Set[str]: The collection of dependencies that are available on PyPI.
    """
    pip_packages = set()
    for module in dependencies:
        try: 
            pkg_resources.get_distribution(module)
            pip_packages.add(module)
        except pkg_resources.DistributionNotFound:
            pass
        except pkg_resources.extern.packaging.requirements.InvalidRequirement:
            pass
    return pip_packages


def parse_local_packages(local_packages: Iterable[str]) -> Set[LocalPackage]:
    """I parse all required information from the local package.

    This enables the usage of the local package on a remote environment.

    Args:
        local_packages (Iterable[str]): A collection of local package names.

    Returns:
        Set[LocalPackage]: A collection of parsed information for each local package
    """