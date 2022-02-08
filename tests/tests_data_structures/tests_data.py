from datetime import datetime, date, timezone
from decimal import Decimal

from tests.utils import TestCase, Dummy

GET_DIFFERENCES_TEST_CASES = [
    TestCase(
        description='Case 0: Complete different new data, type(old_data)==dict, skip_keys=None',
        input={
            'old_data': Dummy(ref_datetime=datetime(2021, 1, 1, 0, 0, tzinfo=timezone.utc)).get_dict_repr(),
            'new_data': {
                'text': 'new_dummy',
                'i_number': 20,
                'f_number': 20.0,
                'd_number': Decimal('20.0'),
                'ref_date': date(2022, 1, 1),
                'ref_datetime': datetime(2022, 1, 1, 0, 0, tzinfo=timezone.utc),
                'bool_type': False
            }
        },
        output={
            'text': 'new_dummy',
            'i_number': 20,
            'f_number': 20.0,
            'd_number': Decimal('20.0'),
            'ref_date': date(2022, 1, 1),
            'ref_datetime': datetime(2022, 1, 1, 0, 0, tzinfo=timezone.utc),
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
            'ref_datetime': datetime(2022, 1, 1, 13, 40, tzinfo=timezone.utc),
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

FINDER_FILTER_TEST_CASES = [
    TestCase(
        description='Case 0: gte operation (>=)',
        input={'i_number__gte': 3},
        output='[T-3, T-4, T-5, T-6]'
    ),
    TestCase(
        description='Case 1: lt operation (<)',
        input={'i_number__lt': 2},
        output='[T-1]'
    ),
    TestCase(
        description='Case 2: lte operation (<=)',
        input={'i_number_lte': 1},
        output='[]'
    ),
    TestCase(
        description='Case 3: ne operation (!=)',
        input={'text__ne': 'T-1'},
        output='[T-2, T-3, T-4, T-5, T-6]'
    ),
    TestCase(
        description='Case 4: in operation',
        input={'i_number__in': [1, 2, 3, 10]},
        output='[T-1, T-2, T-3]'
    ),
    TestCase(
        description='Case 5: as_list= False',
        input={'i_number__in': [1, 2, 3, 10], 'as_list': False},
        output=['T-1', 'T-2', 'T-3']
    )
]

FINDER_FIND_TEST_CASES = [
    TestCase(
        description='Case 0: default operation (=)',
        input={'i_number': 1},
        output='T-1'
    ),
    TestCase(
        description='Case 1: gt operation (>)',
        input={'i_number__gt': 2},
        output='T-3'
    ),
    TestCase(
        description='Case 2: find attr in relation, find: child.text=7, return record obj T-6',
        input={'child.text': 'T-7'},
        output='T-6'
    ),
    TestCase(
        description='Case 3: find attr in relation, attr does not exist, filter will not verify',
        input={'child.not_found': 'T-1'},
        output=None
    ),
    TestCase(
        description='Case 4: filter with ignore_types=True',
        input={'i_number': '1', 'ignore_types': True},
        output='T-1'
    ),
    TestCase(
        description='Case 5: operator not in available ones',
        input={'i_number__not_found': 2},
        output=None
    ),
]

FINDER_FILTER_ON_EMPTY_RECORDS = [
    TestCase(
        description='Case 0: Finder([]) initialized with empty list',
        input={'text': 'T-1'},
        output=None
    )
]
