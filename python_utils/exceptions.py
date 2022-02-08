def re_raise_exception(exception: Exception, *new_args):
    """
    Get an Exception obj and reraise it with extra new passed arguments

    Args:
        exception: Exception obj to be raised
        *new_args: Args to be passed to the exception obj
    Raises:
        The exception obj with the new args attached
    Examples:
        >>> re_raise_exception(Exception('Old exception:'), 'new arg', 'another one')
        Traceback (most recent call last):
        ...
        Exception: ('Old exception:', 'new arg', 'another one')
        >>> re_raise_exception(Exception('Old exception:'))
        Traceback (most recent call last):
        ...
        Exception: Old exception:
    """
    exception.args += tuple(new_args)
    raise exception
