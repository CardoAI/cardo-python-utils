import math
from decimal import Decimal
from numbers import Number
from typing import Optional, Any


def dec_multiply(*args) -> Optional[Decimal]:
    """
    Multiplication of numbers passed as *args.

    Args:
        *args: numbers we want to multiply
    Returns:
        The result of the multiplication as a decimal number
    Examples:
        >>> dec_multiply(3, 3.5, 4, 2.34)
        Decimal('98.280')
        >>> dec_multiply() is None
        True
    """
    if not args:
        return
    total = Decimal(str(args[0]))
    for element in args[1:]:
        total *= Decimal(str(element))
    return total


def dec_sum(*args: Optional[Number]) -> Decimal:
    """
    Sum of numbers passed as *args. Skips None values

    Args:
        *args: numbers we want to sum
    Returns:
        The result of the sum as a decimal number
    Examples:
        >>> dec_sum(20.24, 2.2)
        Decimal('22.44')
        >>> dec_sum(20.24, None, 0, 10)
        Decimal('30.24')
    """
    return sum([Decimal(str(x)) if x is not None else 0 for x in args])


def dec_ratio(value1: Number, value2: Number) -> Optional[Decimal]:
    """
    Decimal ratio against 2 numbers. If value2 is 0 return None

    Args:
        value1: First number, numerator
        value2: Second number, denominator
    Returns:
        The result of ratio as a decimal number
    Examples:
        >>> dec_ratio(20.24, 2.2)
        Decimal('9.2')
        >>> dec_ratio(20.24, 0) is None
        True
    """
    return Decimal(str(value1)) / Decimal(str(value2)) if value2 else None


def dec_subtraction(value1: Optional[Number], value2: Optional[Number]) -> Decimal:
    """
    Decimal subtraction against 2 numbers

    Args:
        value1: First number
        value2: Second number as subtractor
    Returns:
        The result of subtraction as a decimal number
    Examples:
        >>> dec_subtraction(14.3, 3.567)
        Decimal('10.733')
        >>> dec_subtraction(None, None)
        Decimal('0')
    """
    return Decimal(str(value1) if value1 else 0) - Decimal(str(value2) if value2 else 0)


def parse_number(v: str) -> float:
    """
    Parse a given text which may contain commas and dots to float.

    Args:
        v:  str, value to be parsed to float
    Returns:
        v:  float, parsed value
    Examples:
        >>> parse_number('0,00')
        0.0
        >>> parse_number('23.789,90')
        23789.9
        >>> parse_number('23789.80')
        23789.8
        >>> parse_number('23,789.80')
        23789.8
        >>> parse_number('234,234,342.80')
        234234342.8
    """
    if ',' in v:
        if '.' in v:
            if v.find('.') < v.find(','):
                v = float(v.replace('.', '').replace(',', '.'))
            else:
                v = float(v.replace(',', ''))
        else:
            v = float(v.replace(',', '.'))
    else:
        v = float(v)

    return v


def safe_min(*values) -> Optional[Any]:
    """
    Find the min value in a list. Ignore None values.

    Args:
        *values: all values to be compared
    Returns:
         min value in the list or None
    Examples:
        >>> safe_min(None, 5, 2, 1, None, 5)
        1
        >>> safe_min(None, None) is None
        True
    """
    min_value = None
    for value in values:
        if value is None:
            continue
        if min_value is None:
            min_value = value
        elif value < min_value:
            min_value = value
    return min_value


def safe_max(*values) -> Optional[Any]:
    """
    Find the max value in a list. Ignore None values.

    Args:
        *values: all values to be compared
    Returns:
         max value in the list or None
    Examples:
        >>> safe_max(None, 5, 3, 7)
        7
        >>> safe_max(None, None) is None
        True
    """
    max_value = None
    for value in values:
        if value is None:
            continue
        if max_value is None:
            max_value = value
        elif value > max_value:
            max_value = value
    return max_value


def are_equal(number1: Number, number2: Number, precision=6) -> bool:
    """
    Compare two decimal numbers with a given precision

    Args:
        number1: number to be compared
        number2: number which will be used as the comparator
        precision: represent what precision to use when comparing decimal numbers
    Returns:
        True if both are equal or False otherwise
    Examples:
        >>> are_equal(13.44, 13.4, precision=1)
        True
        >>> are_equal(13.44, 13.4)
        False
    """
    return abs(dec_subtraction(number1, number2)) < Decimal(str(1 / (10 ** precision)))


def evaluate(expression: str):
    """
    Evaluate a math expression.

    Args:
        expression: string representing the math expression to be eval()
    Returns:
        result of the math expression from eval()
    Raises:
        NameError: If expression passed is not from math library
    Examples:
        >>> evaluate("5 + 2")
        7
        >>> evaluate("sqrt(9)")
        3.0
        >>> evaluate("hello - hello")
        Traceback (most recent call last):
        ...
        NameError: The use of 'hello' is not allowed
    """

    # Compile the expression
    code = compile(expression, "<string>", "eval")
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}

    # Validate allowed names
    for name in code.co_names:
        if name not in allowed_names:
            raise NameError(f"The use of '{name}' is not allowed")
    return eval(code, {"__builtins__": {}}, allowed_names)
