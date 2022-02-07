from datetime import datetime
from decimal import Decimal
from typing import Callable, Hashable, Generator, \
    Iterable
from typing import List, Any, Dict
from typing import Optional, Union

import pytz as pytz

from helper_module.calculation import are_equal
from helper_module.types_hinting import DictOrObject


def safe_find(records: Iterable, filter_func: Callable) -> Optional[Any]:
    """
    Given a list of dict and a filter function find the first occurrence and return it or None
    if nothing found

    Args:
        filter_func: function that the filter is going to excecuate over the list
        records: list of dict to iterate over
    Returns:
        first occurrence found or None
    Examples:
        >>> safe_find([{'a': 'T', 'b': 'H'}, {'a': 'F'}], lambda rec: rec.get('a') == 'F')
        {'a': 'F'}
        >>> safe_find([{'a': 'T'}], lambda rec: rec.get('a') == 'F') is None
        True
    """
    try:
        return next(filter(filter_func, records))
    except StopIteration:
        return None


def find_by(records: List[Dict], attr: Hashable, value: Any) -> Optional[Dict]:
    """
    Given a list of dict and an attribute, value, return the first occurrence
    where dict[attr] == value or None if no occurrence accomplishes the condition

    Args:
        records: list of dict obj to iterate over
        attr: the attr we're trying to check for
        value: value to make the check against
    Returns:
        Dict record if found or None
    Examples:
        >>> find_by([{'a': 'T', 'b': 'H'}, {'a': 'F'}], attr='b', value='H')
        {'a': 'T', 'b': 'H'}
        >>> find_by([{'a': 'T', 'b': 'H'}, {'a': 'F'}], attr='a', value='Hello') is None
        True
    """
    return safe_find(records, lambda rec: value == rec.get(attr))


def filter_dicts(records: List[Dict], as_list=True, **filters) -> Union[List[Dict], Iterable[Dict]]:
    """
    Pass a list of dict and filters as kwargs to get all filtered records as list or filter obj

    Args:
        records: list of dicts to iterate and filter from
        as_list: Flag that shows if found records should be returned as list
        **filters: kwargs to be used for filtering as key:value pairs
    Returns:
        Filtered records as filter obj or list
    Examples:
        >>> test_d = [{'a': 1, 'b': 2}, {'a': 0, 'b': 3}, {'a': 1, 'd': 3}, {'a': 2, 'd': 3}]
        >>> filter_dicts(test_d,  a=1, d=3)
        [{'a': 1, 'd': 3}]
        >>> filter_dicts(test_d, a=1, b=3, d=3)
        []
        >>> filter_dicts(test_d)
        [{'a': 1, 'b': 2}, {'a': 0, 'b': 3}, {'a': 1, 'd': 3}, {'a': 2, 'd': 3}]
        >>> filter_dicts([{}])
        [{}]
        >>> type(filter_dicts(test_d, as_list=False, a=1))
        <class 'filter'>
        >>> sum(1 for _ in filter_dicts(test_d, as_list=False, a=1))
        2
    """
    filtered_records = filter(
        lambda rec: all([rec.get(key) == value for key, value in filters.items()]), records)
    if as_list:
        filtered_records = list(filtered_records)
    return filtered_records


def filter_objects(objects: List[object], as_list=True, **filters) -> Union[List[object], Iterable[Dict]]:
    """
    Pass a list of objects and filters as kwargs to get all filtered records as list or filter obj

    Args:
        objects: list of objects to iterate and filter from
        as_list: Flag that shows if found records should be returned as list
        **filters: kwargs to be used for filtering as key:value pairs
    Returns:
        Filtered records as filter obj or list
    Examples:
        >>> class A:
        ...     def __init__(self, var1, var2):
        ...         self.var1, self.var2 = var1, var2
        ...     def __repr__(self):
        ...         return f'{self.var1}-{self.var2}'
        ...
        >>> filter_objects([A('test', 1), A('test2', 2)],  var1='test', var2=1)
        [test-1]
        >>> filter_objects([A('test', 1), A('test2', 2)], var1='test', var2=2)
        []
        >>> filter_objects([A('test', 1), A('test2', 2)])
        [test-1, test2-2]
        >>> filter_objects([{}])
        [{}]
        >>> type(filter_objects([A('test', 2), A('test2', 2)], as_list=False, var2=2))
        <class 'filter'>
        >>> sum(1 for _ in filter_objects([A('test', 2), A('test2', 2)], as_list=False, var2=2))
        2
    """
    filtered_objects = filter(
        lambda rec: all([getattr(rec, key) == value for key, value in filters.items()]), objects)
    if as_list:
        filtered_objects = list(filtered_objects)
    return filtered_objects


def find_object(objects: List[object], **filters) -> Optional[object]:
    """
    Pass a list of objects and filters as kwargs to get first occurence record. If no filters
    passed return first object in the list

    Args:
        objects: list of objects to iterate and filter from
        **filters: kwargs to be used for filtering as key:value pairs
    Returns:
        Found record obj or None
    Examples:
        >>> class A:
        ...     def __init__(self, var1, var2, var3=False):
        ...         self.var1, self.var2, self.var3 = var1, var2, var3
        ...     def __repr__(self):
        ...         return f'{self.var1}-{self.var2}'
        ...
        >>> find_object([A('test', 1), A('test2', 2)],  var1='test', var2=1)
        test-1
        >>> find_object([A('test', 1), A('test2', 2)], var1='test', var2=2) is None
        True
        >>> find_object([{}])
        {}
        """
    for rec in objects:
        if all([getattr(rec, key) == value for key, value in filters.items()]):
            return rec


def exclude_keys(dictionary: Dict, keys: List[Hashable]) -> Dict:
    """
    Iterate over a dict and check if key in exclude keys list. If yes, do not append the key:value
    pair in the new dict which is going to be returned.

    Args:
        dictionary: dict holding the items we are going to iterate
        keys: list of dict keys which we don't want to include in the new dict
    Returns:
        New dict without the key:value pairs where keys in passed list of keys
    Examples:
        >>> exclude_keys({'a': 1, 'b': 2}, keys=['a'])
        {'b': 2}
    """
    return {k: v for k, v in dictionary.items() if k not in keys}


def keep_keys(dictionary: Dict, keys: List[Hashable]) -> Dict:
    """
    Iterate over a dict and check if key in include keys list. If yes, append the key:value
    pair in the new dict which is going to be returned.

    Args:
        dictionary: dict holding the items we are going to iterate
        keys: list of dict keys which we want to include in the new dict
    Returns:
        New dict with the key:value pairs where keys in passed list of keys
    Examples:
        >>> keep_keys({'a': 1, 'b': 2}, keys=['a'])
        {'a': 1}
    """
    return {k: v for k, v in dictionary.items() if k in keys}


def exclude_none_values(dictionary: Dict) -> Dict:
    """
    Iterate over a dict and check if value is not None append key:value pair in new dict.

    Args:
        dictionary: dict holding the items we are going to iterate
    Returns:
         New dict with the key:value pairs where values are not None
    Examples:
        >>> exclude_none_values({'a': None, 'b': 1})
        {'b': 1}
    """
    return {k: v for k, v in dictionary.items() if v is not None}


def get_values(dictionary: Dict, keys: List[Hashable], dtypes: Dict = None) -> Dict:
    """
    Get values from dictionary whose keys are in the keys list

    Args:
        dictionary: Dictionary with the values
        keys: List of keys to extract
        dtypes: A mapping of fields to types, used to convert fields
    Returns:
        New dict with the key:value pairs
    Examples:
        >>> get_values({'a': '1', 'b': 2, 'c': '3'}, keys=['a', 'c'], dtypes={'a': int})
        {'a': 1, 'c': '3'}
    """
    data = {}
    for key in keys:
        value = dictionary.get(key)
        # Apply type conversion
        if dtypes and value is not None and dtypes.get(key):
            value = dtypes[key](value)
        data[key] = value
    return data


def get_differences(
        old_data: DictOrObject,
        new_data: Dict,
        skip_keys: List[Hashable] = None,
        number_precision: int = 6
) -> Dict:
    """
    Get a dictionary with the values that have changed between two versions of data.

    Args:
        old_data: Object or dictionary containing the old version of the data
        new_data: Dictionary containing the new version of the data
        skip_keys: Option list of keys to skip during comparison
        number_precision: Precision used for number comparisons
    Returns:
        Dict containing the keys that have changed with the new respective values
    """
    differences = {}
    if not skip_keys:
        skip_keys = []

    old_data_is_dict = isinstance(old_data, dict)

    for key, new_value in new_data.items():
        if key in skip_keys:
            continue

        if old_data_is_dict:
            old_value = old_data[key]
        else:
            old_value = getattr(old_data, key)

        # Process Decimal
        # Process datetime - Add UTC timezone when missing
        if isinstance(old_value, datetime) and not old_value.tzinfo:
            old_value = old_value.replace(tzinfo=pytz.UTC)
        if isinstance(new_value, datetime) and not new_value.tzinfo:
            new_value = new_value.replace(tzinfo=pytz.UTC)

        if isinstance(new_value, (float, Decimal)):
            # Compare numbers taking precision into consideration
            if (old_value is None
                    or not are_equal(old_value, new_value, precision=number_precision)):  # type: ignore
                differences[key] = new_value

        # Compare values
        else:
            if old_value != new_value:
                differences[key] = new_value

    return differences


def have_equal_values(dict1: Dict, dict2: Dict, attributes: List = None) -> bool:
    """
    Compare if the given attributes of two dictionaries are equal.

    Args:
        dict1: dict to be compared
        dict2: dict to be compared against
        attributes: list of keys that are going to compare, default None, check all keys in dict1
    Returns:
        True if dict1 attributes are equal with dict2, False otherwise
    Examples:
        >>> have_equal_values({'a': 1, 'b': 3}, {'a': 1, 'b': 2}, attributes=['a'])
        True
        >>> have_equal_values({'a': 1, 'b': 3}, {'a': 1, 'b': 2})
        False
    """

    if not attributes:
        attributes = dict1.keys()

    for attribute in attributes:
        if dict1.get(attribute) != dict2.get(attribute):
            return False

    return True


def get_nested(dictionary: Union[Dict, Any], *attrs: Hashable) -> Optional[Any]:
    """
    Access a nested dict by passing all the keys we want to access.

    Args:
        dictionary: Dict object we want to access
        *attrs: Keys we want to access
    Returns:
        The value we want to get or None if it can't be found
    Examples:
        >>> get_nested({'a': {'b': {'c': 'Value'}}}, 'a', 'b', 'c')
        'Value'
        >>> get_nested({})
        {}
        >>> get_nested({'a': {'b': {'c': 'Value'}}}, 'a', 'd', 'c') is None
        True
        >>> get_nested(1, 'a') is None
        True
    """
    if not isinstance(dictionary, dict):
        return None

    current_value = dictionary
    for attr in attrs:
        current_value = current_value.get(attr)
        if not isinstance(current_value, dict):
            return current_value
    return current_value


def lists_intersection(list1: List, list2: List) -> List:
    """
    Find the intersection between 2 lists

    Args:
        list1: list to look for intersection
        list2: list to be looked against
    Returns:
        new list with the intersection of the 2 lists
    Examples:
        >>> lists_intersection([1, 2, 3], [2, 3, 4])
        [2, 3]
        >>> lists_intersection([1, 2, 3], [4, 5, 6])
        []
        >>> lists_intersection([1, 'test', 3], [4, 5, 'test'])
        ['test']
    """
    return list(set(list1).intersection(list2))


def chunks(lst: List, chunk: int) -> Generator[List, None, None]:
    """
    Yield successive n-sized chunks from lst.

    Args:
        lst: list to yield chunks from
        chunk: size of the chunk
    Returns:
        list of elements from generator
    Examples:
        >>> a = chunks([1, 2, 3, 4, 5, 6], chunk=2)
        >>> print(type(a))
        <class 'generator'>
        >>> sum(1 for _ in a)
        3
        >>> next(chunks([1, 2, 3, 4, 5, 6], chunk=2))
        [1, 2]
    """
    for i in range(0, len(lst), chunk):
        yield lst[i: i + chunk]


def ints(values: List[str]) -> List[int]:
    """
    Converts elements of a list to ints

    Args:
        values: list of elements to be converted
    Returns:
        list with ints representations of elements
    Examples:
        >>> ints(['1', '2', '3'])
        [1, 2, 3]
    """
    return [int(value) for value in values]


def any_not_none(iterable: Iterable) -> bool:
    """
    The default behaviour of the builtin any function checks the value
    with `if element` and this is causing the values like zero (0) to be
    considered as Falsy values. This function aims to change this behaviour
    to return False only when all the values are None.

    Args:
        iterable: Iterable in which we will look for not None values
    Returns:
        bool value indicating if at least one element is not None
    Examples:
        >>> any_not_none([None, None, 13])
        True
        >>> any_not_none([None, None, 0])
        True
        >>> any_not_none([None])
        False
        >>> any_not_none([])
        False
    """
    for element in iterable:
        if element is not None:
            return True

    return False