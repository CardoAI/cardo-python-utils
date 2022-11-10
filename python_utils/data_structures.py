import operator
from datetime import datetime, timezone
from decimal import Decimal
from typing import (
    Callable, Hashable, Generator, Iterable, List, Any, Dict, Optional, Union
)

from python_utils.math import are_equal
from python_utils.types_hinting import T


def safe_find(records: Iterable, filter_func: Callable) -> Optional[Any]:
    """
    Wrapper around the filter function, to return only the first record when
    there is a match, or None instead.

    Args:
        records: List to iterate over
        filter_func: Function that will be appliead on each record
    Returns:
        First occurrence found or None
    Examples:
        >>> safe_find([{'a': 'T', 'b': 'H'}, {'a': 'F'}], lambda rec: rec.get('a') == 'F')
        {'a': 'F'}
        >>> safe_find([1, 2, 3], lambda rec: rec > 0)
        1
        >>> safe_find([{'a': 'T'}], lambda rec: rec.get('a') == 'F') is None
        True
    """
    try:
        return next(filter(filter_func, records))
    except StopIteration:
        return None


def find_by(records: List[Dict], attr: Hashable, value: Any) -> Optional[Dict]:
    """
    Given a list of dicts and an attribute, value, return the first occurrence
    where dict[attr] == value or None if no occurrence accomplishes the condition

    Args:
        records: list of dicts to iterate over
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
    Pass a list of dicts and filters as kwargs to get all filtered records as list or generator

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


def filter_objects(objects: List[T], as_list=True, **filters) -> Union[List[T], Iterable[T]]:
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


def find_object(objects: List[T], **filters) -> Optional[T]:
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
    Create a new dictionary, excluding the keys given.

    Args:
        dictionary: Source dict
        keys: list of keys which we don't want to include in the new dict
    Examples:
        >>> exclude_keys({'a': 1, 'b': 2}, keys=['a'])
        {'b': 2}
    """
    return {k: v for k, v in dictionary.items() if k not in keys}


def keep_keys(dictionary: Dict, keys: List[Hashable]) -> Dict:
    """
    Create a new dictionary, keeping only the given keys.

    Args:
        dictionary: Source dict
        keys: list of dict keys which we want to include in the new dict
    Examples:
        >>> keep_keys({'a': 1, 'b': 2}, keys=['a'])
        {'a': 1}
    """
    return {k: v for k, v in dictionary.items() if k in keys}


def exclude_none_values(dictionary: Dict) -> Dict:
    """
    Create a new dictionary, removing the keys whose value is None.

    Args:
        dictionary: Source dict
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
        old_data: Union[Dict, T],
        new_data: Dict,
        skip_keys: List[Hashable] = None,
        number_precision: int = 6
) -> Dict:
    """
    Get a dictionary with the values that have changed between two versions of data.

    Args:
        old_data: Object or dictionary containing the old version of the data
        new_data: Dictionary containing the new version of the data
        skip_keys: Optional list of keys to skip during comparison
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
            old_value = old_value.replace(tzinfo=timezone.utc)
        if isinstance(new_value, datetime) and not new_value.tzinfo:
            new_value = new_value.replace(tzinfo=timezone.utc)

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


def get_nested(dictionary: Dict, *attrs: Hashable) -> Optional[Any]:
    """
    Access a nested value in a dict by passing the keys of all the levels.

    Args:
        dictionary: Dict object we want to access
        *attrs: Keys we want to access
    Returns:
        The value we want to get or None if it can't be found
    Raises:
        AttributeError: When the original object or a nested one is not a dict
    Examples:
        >>> get_nested({'a': {'b': {'c': 'Value'}}}, 'a', 'b', 'c')
        'Value'
        >>> get_nested({}, 'a') is None
        True
        >>> get_nested({'a': 'b'}, 'c') is None
        True
        >>> get_nested({'a': {'b': {'c': 'Value'}}}, 'a', 'd', 'c') is None
        True
        >>> get_nested(1, 'a') is None  # type: ignore
        True
    """
    if not dictionary or not attrs:
        return None

    current_value = dictionary
    for attr in attrs:
        try:
            current_value = current_value.get(attr)
        except AttributeError:
            return None
    return current_value


def lists_intersection(list1: List, list2: List) -> List:
    """
    Find the common elements between 2 lists.

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
    Verify if any of the elements of the iterable is not None.
    The default behaviour of the builtin any function checks the value
    with `if element` and causes the values like zero (0) to be
    treated as Falsy values. This function aims to change this behaviour
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


class Finder:
    """
    Finder class to be used for imitating an ORM with dict and objects
    Examples:
        >>> records = [{'id': 1, 'foo': 'bar'}, {'id': 2, 'a': 'b'}]
        >>> Finder(records).find(id=1)
        {'id': 1, 'foo': 'bar'}
        >>> Finder(records).filter(foo='bar')
        [{'id': 1, 'foo': 'bar'}]
    """
    ops = {
        "gt": operator.gt,
        "gte": operator.ge,
        "lt": operator.lt,
        "lte": operator.le,
        "eq": operator.eq,
        "ne": operator.ne,
        "in": lambda item, iterable: item in iterable,
    }
    available_ops = ops.keys()

    def __init__(self, records: List[Union[Dict, T]]):
        self._records = records

    @classmethod
    def _compare(cls, value1: Any, op: str, value2: Any, ignore_types=False) -> bool:
        if ignore_types:
            value1 = str(value1)
            value2 = str(value2)
        return cls.ops[op](value1, value2)

    @classmethod
    def _verify(cls, record: Union[Dict, T], ignore_types=False, **checks) -> bool:
        """
        Verify that the record fulfills the given checks.

        Args:
            record: The record to be verified: dict or object
            ignore_types: If True, compare the values as strings
            **checks: Dictionary with checks in the form: {"attr__gt": 5}

        Returns:
            True if the record passes *all* the checks, False otherwise
        """
        for key, value in checks.items():
            if "__" in key:
                elements = key.split("__")
                # If operator has been declared
                if elements[-1] in cls.available_ops:
                    attr = ".".join(elements[:-1])
                    op = elements[-1]
                # eq operator by default
                else:
                    attr = ".".join(elements)
                    op = "eq"
            else:
                attr = key
                op = "eq"
            if not cls._compare(cls._get_value(record, attr), op, value, ignore_types):
                return False
        return True

    @staticmethod
    def _get_value(record: Union[Dict, T], attr: str) -> Optional[Any]:
        """
        Get the value of the attribute for the given record. Used to process dicts and objects uniformly.

        Args:
            record: The record from which the value will be retrieved. Can be a dict or an object
            attr: The attribute to retrieve value. For objects, supports syntax like 'asset__debtor__country_id'.
        Returns:
            Value found or None
        """
        if isinstance(record, dict):
            return record.get(attr)
        else:
            try:
                while "." in attr:
                    current_attr, attr = attr.split(".", 1)
                    record = getattr(record, current_attr)
                return getattr(record, attr)
            except AttributeError:
                return None

    def filter(self, as_list=True, ignore_types=False, **filters):
        filtered_records = filter(lambda rec: self._verify(rec, ignore_types, **filters), self._records)
        if as_list:
            filtered_records = list(filtered_records)
        return filtered_records

    def find(self, **filters):
        for record in self._records:
            if self._verify(record, **filters):
                return record
