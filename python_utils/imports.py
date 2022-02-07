from importlib import import_module


def import_optional_dependency(module_to_import: str, dependency: str = None):
    """
    Attempt to import a module from an external dependency.
    Raise an error if that dependency is not installed.
    Args:
        module_to_import: A string containing the module to be imported
        dependency: Information about the dependency required
    Raises:
        ModuleNotFoundError: If the dependency is not installed
    Examples:
        >>> math = import_optional_dependency('math')
        >>> pyyaml = import_optional_dependency("pyyaml")
        Traceback (most recent call last):
        ...
        ModuleNotFoundError: pyyaml is required to use this function.
    """
    try:
        return import_module(module_to_import)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"{dependency or module_to_import} is required to use this function.")
