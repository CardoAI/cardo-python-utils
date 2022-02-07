from importlib import import_module


# todo-remove pragma once used
def import_optional_dependency(module_to_import: str, dependency: str):  # pragma no cover
    """
    Attempt to import a module from an external dependency.
    Raise an error if that dependency is not installed.
    Args:
        module_to_import: A string containing the module to be imported
        dependency: Information about the dependency required
    Raises:
        ModuleNotFoundError: If the dependency is not installed
    """
    try:
        return import_module(module_to_import)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"{dependency} is required to use this function.")
