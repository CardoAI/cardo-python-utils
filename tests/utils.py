from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Any, NamedTuple

from model_utils import Choices

SECTOR_LABELS = Choices(
    (0, 'unknown', 'Unknown'),
    (1, 'sec_a', 'Sector A'),
    (2, 'sec_b', 'Sector B'),
    (3, 'sec_c', 'Sector C'),
)


class Dummy:
    """
    Dummy class to be used by tests.
    """

    def __init__(self,
                 text: str = 'dummy',
                 i_number: Optional[int] = 10,
                 f_number: float = 10.0,
                 d_number: Decimal = Decimal('10.5'),
                 ref_date: date = date(2021, 1, 10),
                 ref_datetime: datetime = datetime(2021, 1, 10, 0, 0),
                 bool_type: bool = True,
                 child=None):
        self.text = text
        self.i_number = i_number
        self.f_number = f_number
        self.d_number = d_number
        self.ref_date = ref_date
        self.ref_datetime = ref_datetime
        self.bool_type = bool_type
        self.child: Optional[Dummy] = child

    def get_dict_repr(self):
        return {
            'text': self.text,
            'i_number': self.i_number,
            'f_number': self.f_number,
            'd_number': self.d_number,
            'ref_date': self.ref_date,
            'ref_datetime': self.ref_datetime,
            'bool_type': self.bool_type
        }

    def __repr__(self):
        return f'{self.text}'


class TestCase(NamedTuple):
    input: Any
    output: Any
    description: str = None
