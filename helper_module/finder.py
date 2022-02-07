import operator
from typing import List, Any, Optional

from helper_module.types_hinting import DictOrObject


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

    def __init__(self, records: List[DictOrObject]):
        self._records = records

    @classmethod
    def _compare(cls, value1: Any, op: str, value2: Any, ignore_types=False) -> bool:
        if ignore_types:
            value1 = str(value1)
            value2 = str(value2)
        return cls.ops[op](value1, value2)

    @classmethod
    def _verify(cls, record: DictOrObject, ignore_types=False, **checks) -> bool:
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
    def _get_value(record: DictOrObject, attr: str) -> Optional[Any]:
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
