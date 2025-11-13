"""
This module contains the ChoiceEnum class, which is a subclass of Enum.
It adds some useful methods to the Enum class, such as:
    - get_by_value
    - list_as
    - mappings
    - comparison methods etc.
"""

from abc import ABC, abstractmethod
from enum import EnumMeta, Enum


class IChoice(ABC):
    @classmethod
    @abstractmethod
    def get_by_value(cls, value):
        """Get element by value"""

    @classmethod
    @abstractmethod
    def list_as(cls, item_type):
        """List choices as"""


class ChoiceEnumMeta(EnumMeta, IChoice, ABC):
    def __new__(mcls, *args, **kwargs):
        new_cls = super().__new__(mcls, *args, **kwargs)

        # Make sure that the int values are unique
        unique_values = set()
        duplicate_values = set()
        for el in new_cls.list_as(int):
            if el in unique_values:
                duplicate_values.add(str(el))
            else:
                unique_values.add(el)

        if duplicate_values:
            raise ValueError(f"Duplicate int values in {new_cls.__name__}: {', '.join(duplicate_values)}")

        return new_cls

    def __contains__(cls, item: int | str) -> bool:
        if isinstance(item, int):
            member_values = [v.value[0] for v in cls.__members__.values()]
        elif isinstance(item, str):
            item = item.lower()
            member_values = [v.value[1].lower() for v in cls.__members__.values()]
        else:
            member_values = cls.__members__.values()

        return item in member_values


class ChoiceEnum(Enum, metaclass=ChoiceEnumMeta):
    def __str__(self) -> str:
        return self.value[1]

    def __int__(self) -> int:
        return self.value[0]

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, int):
            return int(self) == other
        return self is other

    def __hash__(self):
        return hash(f"{self.value[0]}{self.value[1]}")

    @classmethod
    def mappings(cls):
        return {elm.value[0]: elm.value[1] for elm in cls}

    @classmethod
    def get_by_value(cls, value: str | int):
        value_index = 0 if isinstance(value, int) else 1
        return next((v for v in cls.__members__.values() if v.value[value_index] == value), None)

    @classmethod
    def list_as(cls, item_type) -> list[int | str]:
        if item_type not in [int, str]:
            raise TypeError('Invalid item type')
        return list(map(item_type, cls))
