import hashlib
import re
from typing import Optional, List, Any

from python_utils.types_hinting import NumberIFD


def format_percent(value: Optional[NumberIFD]):
    """
    Get value and return a % repr

    Args:
        value: value to be used for % repr
    Returns:
        A % repr of the passed value
    Examples:
        >>> format_percent(13)
        '1300%'
        >>> format_percent(0.13)
        '13.0%'
        >>> from decimal import Decimal
        >>> format_percent(Decimal('0.123456'))
        '12.35%'
    """
    return f"{round(value * 100, 2)}%"


def format_currency(value: Optional[NumberIFD], symbol: str) -> Optional[str]:
    """
    Get value and number and return a currency representation

    Args:
        value:
        symbol: string representing the symbol of currency
    Returns:
        string representing currency and value
    Examples:
        >>> format_currency(120.1234, 'EUR')
        'EUR120.12'
        >>> from decimal import Decimal
        >>> format_currency(Decimal('120.1234'), 'EUR')
        'EUR120.12'
        >>> format_currency(None, 'EUR') is None
        True
    """
    if not value:
        return None
    return f"{symbol}{round(value, 2):,}"


def human_string(text: str) -> str:
    """
    Transform text to human string

    Args:
        text: string to be converted
    Returns:
        converted string
    Examples:
        >>> human_string('test_str')
        'Test Str'
        >>> human_string("")
        ''
    """
    if not text:
        return ""
    return " ".join(word.title() for word in text.split("_"))


camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_case_to_snake_case(text: str) -> str:
    """
    Convert camel case string to snake case, Substitute spaces with _

    Args:
        text: string to be converted
    Returns:
        converted string
    Examples:
        >>> camel_case_to_snake_case('TestStrHello')
        'test_str_hello'
        >>> camel_case_to_snake_case('Test Str Hello  dummy CAPITAL12')
        'test__str__hello__dummy__c_a_p_i_t_a_l12'
    """
    return camel_case_pattern.sub("_", text.replace(" ", "_")).lower()


# Indicates 1 or more spaces
spaces_pattern = re.compile(r" +")


def human_string_to_snake_case(text: str) -> str:
    """
    Transform text from human string to snake case

    Args:
        text: string to be converted
    Returns:
        converted string
    Examples:
        >>> human_string_to_snake_case('Test Str TEST')
        'test_str_test'
    """
    return spaces_pattern.sub("_", text.strip().lower())


def extract_with_pattern(text: str, pattern: str) -> Optional[str]:
    """
    Return the first found result of a given pattern in the string or None if not found
    E.g: ('Test _t Test _t', '_t') -> '_t'

    Args:
        text: string to find the match
        pattern: pattern against which the string is trying to match
    Returns:
        First result of given pattern or None
    Examples:
        >>> extract_with_pattern('Test _t Test _t', '_t')
        '_t'
        >>> extract_with_pattern('Test _t Test _t', 'A') is None
        True
        >>> extract_with_pattern('Test 123', '\\d+')
        '123'
    """
    compiled_pattern = re.compile(pattern)
    results = compiled_pattern.search(text)
    if results:
        return results.group(0)


def create_hash(data: List[Any]) -> str:
    """
    Given a list of params calculate a hash based on their values

    Args:
        data: list of params to be used for the hash
    Returns:
        calculated hash value
    Examples:
        >>> create_hash(['test', 'hash', 1])
        '5ca1b365312e58a36bb985fc770a490b'
    """
    merged_data = "-".join([str(rec) for rec in data])
    return hashlib.md5(merged_data.encode("utf-8")).hexdigest()
