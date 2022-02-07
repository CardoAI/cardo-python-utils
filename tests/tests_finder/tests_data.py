from tests.utils import TestCase

FILTER_TEST_CASES = [
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
FIND_TEST_CASES = [
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
FILTER_ON_EMPTY_RECORDS = [
    TestCase(
        description='Case 0: Finder([]) initialized with empty list',
        input={'text': 'T-1'},
        output=None
    )
]
