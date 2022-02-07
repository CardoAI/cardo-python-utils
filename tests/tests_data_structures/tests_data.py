from datetime import datetime, date
from decimal import Decimal

import pytz

from tests.utils import TestCase, Dummy

GET_DIFFERENCES_TEST_CASES = [
    TestCase(
        description='Case 0: Complete different new data, type(old_data)==dict, skip_keys=None',
        input={
            'old_data': Dummy(ref_datetime=datetime(2021, 1, 1, 0, 0, tzinfo=pytz.UTC)).get_dict_repr(),
            'new_data': {
                'text': 'new_dummy',
                'i_number': 20,
                'f_number': 20.0,
                'd_number': Decimal('20.0'),
                'ref_date': date(2022, 1, 1),
                'ref_datetime': datetime(2022, 1, 1, 0, 0, tzinfo=pytz.UTC),
                'bool_type': False
            }
        },
        output={
            'text': 'new_dummy',
            'i_number': 20,
            'f_number': 20.0,
            'd_number': Decimal('20.0'),
            'ref_date': date(2022, 1, 1),
            'ref_datetime': datetime(2022, 1, 1, 0, 0, tzinfo=pytz.UTC),
            'bool_type': False
        }
    ),
    TestCase(
        description='Case 1: Some differences in new data, with skip_keys',
        input={
            'old_data': Dummy(),
            'new_data': {
                'text': 'new_dummy',
                'i_number': 100,
                'f_number': 10.0
            },
            'skip_keys': ['i_number']
        },
        output={
            'text': 'new_dummy',
        },
    ),
    TestCase(
        description='Case 2: Some differences in new data, type(old_data)==object',
        input={
            'old_data': Dummy(i_number=None),
            'new_data': Dummy(
                text='new_dummy',
                i_number=20,
                f_number=20.0,
                d_number=Decimal('20.0'),
                ref_date=date(2022, 1, 1),
                ref_datetime=datetime(2022, 1, 1, 13, 40),
                bool_type=False).get_dict_repr()
        },
        output={
            'text': 'new_dummy',
            'i_number': 20,
            'f_number': 20.0,
            'd_number': Decimal('20.0'),
            'ref_date': date(2022, 1, 1),
            'ref_datetime': datetime(2022, 1, 1, 13, 40, tzinfo=pytz.UTC),
            'bool_type': False
        },
    ),
    TestCase(
        description='Case 3: Different new data with number_precision passed',
        input={
            'old_data': Dummy(),
            'new_data': Dummy(f_number=10.001, d_number=Decimal('10.51')).get_dict_repr(),
            'skip_keys': ['ref_datetime'],
            'number_precision': 2
        },
        output={'d_number': Decimal('10.51')}
    ),
]
