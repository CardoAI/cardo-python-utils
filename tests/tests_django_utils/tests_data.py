from datetime import date

from tests.testapp.models import Invoice, Company
from tests.utils import TestCase, SECTOR_LABELS

RECORD_TO_DICT_TEST_CASES = [
    TestCase(
        description='Case 0: exclude=None',
        input={'record': Invoice(code='Test', amount=100, issue_date='2021-1-1')},
        output={'active': True, 'amount': 100, 'code': 'Test', 'company_id': None, 'created_at': None, 'f_amount': None,
                'history_info': {}, 'id': None, 'issue_date': '2021-1-1', 'sector_label': 'Unknown', 'tax': 5,
                'updated_at': None},
    ),
    TestCase(
        description='Case 1: Passing exclude list',
        input={
            'record': Invoice(code='Test', amount=100, issue_date='2021-1-1'),
            'exclude': ['issue_date', 'sector_label', 'updated_at', 'company_id', 'tax', 'history_info', 'created_at',
                        'f_amount', 'active']
        },
        output={'id': None, 'code': 'Test', 'amount': 100},
    )
]
PERFORM_QUERY_TEST_CASES = [
    TestCase(
        description='Case 0: Select * query',
        input={'sql_query': 'SELECT id, amount, code, issue_date, sector_label, company_id  FROM test_invoice'},
        output=[
            {'amount': 0, 'code': 'T-0', 'id': 1, 'issue_date': date(2021, 1, 1), 'sector_label': 0,
             'company_id': None},
            {'amount': 100, 'code': 'T-1', 'id': 2, 'issue_date': date(2021, 1, 1), 'sector_label': 0,
             'company_id': None},
            {'amount': 200, 'code': 'T-2', 'id': 3, 'issue_date': date(2021, 1, 1), 'sector_label': 0,
             'company_id': None}
        ],
    ),
    TestCase(
        description='Case 1: with params',
        input={'sql_query': 'SELECT SUM(amount) as total_amount FROM test_invoice where amount > %s',
               'params': [50]},
        output=[{'total_amount': 300}],
    ),
    TestCase(
        description='Case 2: expected_results=False',
        input={'sql_query': 'SELECT COUNT(*) FROM test_invoice', 'expected_results': False},
        output=None,
    )
]
GET_TOTAL_TEST_CASES = [
    TestCase(
        description='Case 0: With queryset',
        input={'records': Invoice.objects.all(), 'aggregation_field': 'amount'},
        output=300
    ),
    TestCase(
        description='Case 1: Empty queryset',
        input={'records': Invoice.objects.filter(id=100), 'aggregation_field': 'amount'},
        output=None,
    )
]
GET_MIN_TEST_CASES = [
    TestCase(
        description='Case 0: With queryset',
        input={'records': Invoice.objects.all(), 'aggregation_field': 'amount'},
        output=0
    ),
    TestCase(
        description='Case 1: Empty queryset',
        input={'records': Invoice.objects.filter(id=100), 'aggregation_field': 'amount'},
        output=None
    )
]
GET_AVERAGE_TEST_CASES = [
    TestCase(
        description='Case 0: With queryset',
        input={'records': Invoice.objects.all(), 'aggregation_field': 'amount'},
        output=100
    ),
    TestCase(
        description='Case 1: Empty queryset',
        input={'records': Invoice.objects.filter(id=100), 'aggregation_field': 'amount'},
        output=None
    )
]
GET_MAX_TEST_CASES = [
    TestCase(
        description='Case 0: With queryset',
        input={'records': Invoice.objects.all(), 'aggregation_field': 'amount'},
        output=200
    ),
    TestCase(
        description='Case 1: Empty queryset',
        input={'records': Invoice.objects.filter(id=100), 'aggregation_field': 'amount'},
        output=None
    ),
]
GET_CHOICE_VALUE_TEST_CASES = [
    TestCase(
        description='Case 0: existing human string',
        input={'choices': SECTOR_LABELS, 'human_string': 'Sector A'},
        output=1
    ),
    TestCase(
        description='Case 1: not found db repr for human string',
        input={'choices': SECTOR_LABELS, 'human_string': 'Not Found'},
        output=None
    )
]
GET_ID_FIELD_MAP_TEST_CASES = [
    TestCase(
        description='Case 0: Get mapping of code field',
        input={'queryset': Invoice.objects.all(), 'field': 'code'},
        output={1: 'T-0', 2: 'T-1', 3: 'T-2'}
    )
]
CALL_PROCEDURE_TEST_CASES = [
    TestCase(
        description='Case 0: no params',
        input={'procedure_name': 'hello'},
        output={'sql_query': 'call hello();', 'params': None, 'expected_results': False}
    ),
    TestCase(
        description='Case 1: passed params',
        input={'procedure_name': 'hello', 'params': ['code', 1, False]},
        output={'sql_query': 'call hello(%s,%s,%s);', 'params': ['code', 1, False], 'expected_results': False}
    )
]
GET_MODEL_FIELD_NAMES_TEST_CASES = [
    TestCase(
        description='Case 0: model: Invoice',
        input={'model': Invoice},
        output=['id', 'code', 'amount', 'f_amount', 'tax', 'issue_date', 'sector_label', 'updated_at', 'company',
                'active', 'history_info', 'created_at']
    ),
]
IDS_TEST_CASES = [
    TestCase(
        description='Case 0: get ids',
        input={'queryset': Invoice.objects.all()},
        output=[1, 2, 3, 4]
    ),
    TestCase(
        description='Case 1: get codes',
        input={'queryset': Invoice.objects.all(), 'attr': 'code'},
        output=['T-0', 'T-1', 'T-2']
    ),
]
UPDATE_RECORD_SAVE_TRUE_TEST_CASES = [
    TestCase(
        description='Case 0: no data',
        input={'id': 1},
        output='T-0'
    ),

    TestCase(
        description='Case 1: passing data',
        input={'id': 1, 'code': 'updated'},
        output='updated'
    ),
]
COMPUTE_WEIGHTED_AVERAGE_TEST_CASES = [
    TestCase(
        description='Case 0: Default behaviour',
        input={
            'records': Invoice.objects.all(),
            'field': 'amount',
            'weight': 'tax',
        },
        output=100
    ),
    TestCase(
        description='Case 1: is_weight_subquery: True',
        input={
            'records': Invoice.objects.all(),
            'field': 'amount',
            'is_weight_subquery': True,
        },
        output=100
    ),
    TestCase(
        description='Case 2: yes is_field_subquery:True',
        input={
            'records': Invoice.objects.all(),
            'weight': 'tax',
            'is_field_subquery': True,
        },
        output=100
    ),
    TestCase(
        description='Case 3: is_field_subquery:True, is_weight_subquery: True',
        input={
            'records': Invoice.objects.all(),
            'is_field_subquery': True,
            'is_weight_subquery': True,
        },
        output=100
    ),
]
COMPUTE_GROUPED_WEIGHTED_AVERAGE_TEST_CASES = [
    TestCase(
        description='Case 0: Default behaviour, group_by empty list',
        input={
            'records': Invoice.objects.all(),
            'field': 'amount',
            'weight': 'tax',
            'group_by': [],
        },
        output={'count': 3, 'avg': [0, 100, 200]}
    ),
    TestCase(
        description='Case 1: Default behaviour, group_by list',
        input={
            'records': Invoice.objects.all(),
            'field': 'amount',
            'weight': 'tax',
            'group_by': ['sector_label'],
        },
        output={'count': 1, 'avg': [100]}
    ),
]
COMPUTE_GROUPED_WEIGHTED_AVERAGE_SUBQUERY_TEST_CASES = [
    TestCase(
        description='Case 0: Default behaviour',
        input={
            'records': Invoice.objects.all(),
            'group_by': ['sector_label'],
        },
        output={'count': 1, 'avg': 100}
    ),
]
GET_FIELDS_CONFIG_AND_VALUES = [
    TestCase(
        description='Case 0: default behaviour',
        input={'excluded_fields': ['tax']},
        output=[{'name': 'id', 'type': 'integer', 'description': '', 'input': True, 'value': 10},
                {'name': 'code', 'type': 'string', 'description': '', 'input': True, 'value': 'T-10'},
                {'name': 'amount', 'type': 'amount', 'description': '', 'input': True, 'value': 100},
                {'name': 'f_amount', 'type': 'float', 'description': '', 'input': True, 'value': None},
                {'name': 'issue_date', 'type': 'date', 'description': '', 'input': True,
                 'value': date(2021, 1, 1)}, {'name': 'sector_label', 'type': 'selection', 'description': '',
                                              'choices': [{'id': 0, 'name': 'Unknown'},
                                                          {'id': 1, 'name': 'Sector A'},
                                                          {'id': 2, 'name': 'Sector B'},
                                                          {'id': 3, 'name': 'Sector C'}], 'input': True,
                                              'value': 0},
                {'name': 'updated_at', 'type': 'date', 'description': '', 'input': True,
                 'value': None},
                {'name': 'company', 'type': 'selection', 'description': 'company this invoice belongs to',
                 'choices': [{'id': 15, 'name': 'C-15'}], 'input': True, 'value': 15},
                {'name': 'active', 'type': 'bool', 'description': '', 'input': True, 'value': True},
                {'name': 'history_info', 'type': 'json', 'description': '', 'input': True, 'value': {}},
                {'name': 'created_at', 'type': 'datetime', 'description': '', 'input': True, 'value': None}]
    ),
]
GET_MODEL_FIELDS_CONFIG_TEST_CASES = [
    TestCase(
        description='Case 0: Default behaviour',
        input={'model': Company, 'excluded_fields': None, 'read_only_fields': None},
        output=[{'name': 'invoice', 'type': None, 'description': '', 'input': True},
                {'name': 'id', 'type': 'integer', 'description': '', 'input': True},
                {'name': 'name', 'type': 'string', 'description': '', 'input': True}]
    ),
    TestCase(
        description='Case 1: Exclude fields: None',
        input={'model': Company, 'excluded_fields': None, 'read_only_fields': ['id']},
        output=[{'name': 'invoice', 'type': None, 'description': '', 'input': True},
                {'name': 'id', 'type': 'integer', 'description': '', 'input': False},
                {'name': 'name', 'type': 'string', 'description': '', 'input': True}]
    ),
    TestCase(
        description='Case 2: Read only fields: None',
        input={'model': Company, 'excluded_fields': ['invoice'], 'read_only_fields': None},
        output=[{'name': 'id', 'type': 'integer', 'description': '', 'input': True},
                {'name': 'name', 'type': 'string', 'description': '', 'input': True}]
    ),
    TestCase(
        description='Case 3:  excluded_fields and read_only_fields',
        input={'model': Company, 'excluded_fields': ['invoice'], 'read_only_fields': ['id']},
        output=[{'name': 'id', 'type': 'integer', 'description': '', 'input': False},
                {'name': 'name', 'type': 'string', 'description': '', 'input': True}]
    ),
]
SAFE_BULK_CREATE_TEST_CASES = [
    TestCase(
        description='Case 0: no records',
        input=[],
        output=None
    ),
    TestCase(
        description='Case 1: passing data',
        input={
            'invoices': [Invoice(id=i + 1, code=f'T-{i}', amount=i * 100, issue_date=date(2021, 1, 1)) for i in
                         range(3)],
            'companies': [],
            'refresh_fields': None
        },
        output={'created_inv_nr': 3, 'created_comp_nr': 0}
    ),
    TestCase(
        description='Case 2: passing data with foreign keys relations',
        input={
            'invoices': [Invoice(id=i + 1, code=f'T-{i}', amount=i * 100, issue_date=date(2021, 1, 1)) for i in
                         range(3)],
            'companies': [Company(id=i + 1, name=f'C-{i}') for i in range(2)],
            'refresh_fields': ['company', 'not_found']
        },
        output={'created_inv_nr': 3, 'created_comp_nr': 2}
    ),
]
SAFE_BULK_UPDATE_TEST_CASES = [
    TestCase(
        description='Case 0: no records',
        input={'model': Invoice, 'records': [], 'fields': []},
        output=None
    ),
    TestCase(
        description='Case 1: no foreign key update',
        input={
            'model': Invoice,
            'records': [Invoice(id=i + 1, code=f'updated') for i in range(3)],
            'fields': ['code'],
            'refresh_fields': None
        },
        output={
            'old_codes': ['T-0', 'T-1', 'T-2'],
            'new_codes': ['updated', 'updated', 'updated'],
            'old_c_names': ['C1', 'C1', 'C1'],
            'new_c_names': ['C1', 'C1', 'C1'],
        }
    ),
    TestCase(
        description='Case 2: foreign key update',
        input={
            'model': Invoice,
            'records': [Invoice(id=i + 1, code=f'updated') for i in range(3)],
            'fields': ['code', 'company'],
            'refresh_fields': ['company', 'not_found_key']
        },
        output={
            'old_codes': ['T-0', 'T-1', 'T-2'],
            'new_codes': ['updated', 'updated', 'updated'],
            'old_c_names': ['C1', 'C1', 'C1'],
            'new_c_names': ['CN2', 'CN2', 'CN2'],
        }
    ),
]