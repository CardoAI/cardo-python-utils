from decimal import Decimal
from typing import Dict, Union, TypeVar

from django.db.models import Model

DictOrObject = Union[Dict, object]

NumberIFD = Union[int, float, Decimal]
Model_T = TypeVar('Model_T', bound=Model)
