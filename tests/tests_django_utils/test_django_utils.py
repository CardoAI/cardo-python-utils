from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Subquery

from python_utils.django_utils import record_to_dict, perform_query, get_total, get_min, get_average, get_max, \
    get_choice_value, get_or_none, get_id_field_map, get_model_field_names, call_procedure, generate_file_from_buffer, \
    ids, update_record, compute_weighted_average, compute_grouped_weighted_average, \
    compute_grouped_weighted_average_subquery, get_fields_config_and_values, get_model_fields_config, safe_bulk_create, \
    safe_bulk_update
from tests.testapp.models import Invoice, Company
from tests.tests_django_utils.tests_data import RECORD_TO_DICT_TEST_CASES, PERFORM_QUERY_TEST_CASES, \
    GET_TOTAL_TEST_CASES, GET_MIN_TEST_CASES, GET_AVERAGE_TEST_CASES, GET_MAX_TEST_CASES, GET_CHOICE_VALUE_TEST_CASES, \
    GET_ID_FIELD_MAP_TEST_CASES, CALL_PROCEDURE_TEST_CASES, GET_MODEL_FIELD_NAMES_TEST_CASES, IDS_TEST_CASES, \
    UPDATE_RECORD_SAVE_TRUE_TEST_CASES, COMPUTE_WEIGHTED_AVERAGE_TEST_CASES, \
    COMPUTE_GROUPED_WEIGHTED_AVERAGE_TEST_CASES, COMPUTE_GROUPED_WEIGHTED_AVERAGE_SUBQUERY_TEST_CASES, \
    GET_FIELDS_CONFIG_AND_VALUES, GET_MODEL_FIELDS_CONFIG_TEST_CASES, SAFE_BULK_CREATE_TEST_CASES, \
    SAFE_BULK_UPDATE_TEST_CASES


@pytest.mark.parametrize('test_data', RECORD_TO_DICT_TEST_CASES)
def test_record_to_dict(test_data):
    assert test_data.output == record_to_dict(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', PERFORM_QUERY_TEST_CASES)
def test_perform_query(test_data, initial_invoices):
    assert test_data.output == perform_query(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_TOTAL_TEST_CASES)
def test_get_total(test_data, initial_invoices):
    assert test_data.output == get_total(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_MIN_TEST_CASES)
def test_get_min(test_data, initial_invoices):
    assert test_data.output == get_min(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_AVERAGE_TEST_CASES)
def test_get_average(test_data, initial_invoices):
    assert test_data.output == get_average(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_MAX_TEST_CASES)
def test_get_max(test_data, initial_invoices):
    assert test_data.output == get_max(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.parametrize('test_data', GET_CHOICE_VALUE_TEST_CASES)
def test_get_choice_value(test_data):
    assert test_data.output == get_choice_value(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.django_db
def test_get_or_none(initial_invoices):
    assert 1 == get_or_none(Invoice.objects, id=1).id, 'Wrong object was returned'

    assert get_or_none(Invoice.objects, id=100) is None, 'Wrong object was returned'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_ID_FIELD_MAP_TEST_CASES)
def test_get_id_field_map(test_data, initial_invoices):
    assert test_data.output == get_id_field_map(**test_data.input), \
        'Wrong output from function!'


@pytest.mark.parametrize('test_data', CALL_PROCEDURE_TEST_CASES)
def test_call_procedure(test_data):
    with patch('python_utils.django_utils.perform_query') as mocked:
        call_procedure(**test_data.input)
        mocked.assert_called_with(**test_data.output)


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_MODEL_FIELD_NAMES_TEST_CASES)
def test_get_model_field_names(test_data, initial_invoices):
    assert test_data.output == get_model_field_names(**test_data.input), 'Wrong output from function!'


def test_generate_file_from_buffer():
    file = generate_file_from_buffer(file_buffer_io=StringIO('test'), content_type='text/csv', filename='test.csv')
    assert file is not None, 'InMemoryUploadedFile was not created!'
    assert type(file) == InMemoryUploadedFile


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', IDS_TEST_CASES)
def test_ids(test_data, initial_invoices):
    # create an extra record with an existing code to check if functions is returning correct output
    Invoice.objects.get_or_create(id=4, code='T-2', amount=100, issue_date=date(2021, 1, 1))
    print(Invoice.objects.count())
    assert test_data.output == ids(**test_data.input)


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', UPDATE_RECORD_SAVE_TRUE_TEST_CASES)
def test_update_record_save_true(test_data, initial_invoices):
    inv = Invoice.objects.get(id=test_data.input.pop('id'))
    assert test_data.output == update_record(record=inv, **test_data.input).code, 'Wrong output from function!'


@pytest.mark.django_db
def test_update_record_save_false(initial_invoices):
    inv = Invoice.objects.get(id=1)
    u_inv = update_record(record=inv, code='updated', save=False)
    re_fetched_inv = Invoice.objects.get(id=1)
    assert re_fetched_inv.code != u_inv.code


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', COMPUTE_WEIGHTED_AVERAGE_TEST_CASES)
def test_compute_weighted_average(test_data, initial_invoices):
    if test_data.input.get('is_field_subquery'):
        test_data.input['field'] = Invoice.objects.filter(amount=100).values('amount')[:1]
    if test_data.input.get('is_weight_subquery'):
        test_data.input['weight'] = Invoice.objects.all().values('tax')[:1]
    assert test_data.output == compute_weighted_average(**test_data.input), 'Wrong output from function!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', COMPUTE_GROUPED_WEIGHTED_AVERAGE_TEST_CASES)
def test_compute_grouped_weighted_average(test_data, initial_invoices):
    output = compute_grouped_weighted_average(**test_data.input)
    assert test_data.output['count'] == output.count(), 'Wrong output from function!'
    for i, item in enumerate(output):
        assert test_data.output['avg'][i] == item['avg'], 'Wrong output from function!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', COMPUTE_GROUPED_WEIGHTED_AVERAGE_SUBQUERY_TEST_CASES)
def test_compute_grouped_weighted_average_subquery(test_data, initial_invoices):
    test_data.input['field_subquery'] = Subquery(Invoice.objects.filter(amount=100).values('amount')[:1])
    test_data.input['weight_subquery'] = Subquery(Invoice.objects.filter(amount=100).values('amount')[:1])
    output = compute_grouped_weighted_average_subquery(**test_data.input)
    assert test_data.output['count'] == output.count(), 'Wrong output from function!'
    for item in output:
        assert test_data.output['avg'] == item['avg'], 'Wrong avg output from function'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_FIELDS_CONFIG_AND_VALUES)
def test_get_fields_config_and_values(test_data):
    comp = Company.objects.create(id=15, name='C-15')
    inv = Invoice.objects.create(id=10, code='T-10', amount=100, issue_date=date(2021, 1, 1), company=comp)
    assert test_data.output == get_fields_config_and_values(**test_data.input, record=inv), \
        'Wrong output!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', GET_MODEL_FIELDS_CONFIG_TEST_CASES)
def test_get_model_fields_config(test_data):
    assert test_data.output == get_model_fields_config(**test_data.input), 'Wrong test output!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', SAFE_BULK_CREATE_TEST_CASES)
def test_safe_bulk_create(test_data):
    if test_data.output is None:
        safe_bulk_create(model=Invoice, records=test_data.input)
        assert Invoice.objects.count() == 0, 'Invoice objects were created when empty list of data was passed!'
    else:
        invoices = test_data.input['invoices']
        companies = test_data.input['companies']
        if companies:
            # prepare the connection of objects referencing to each-other before we do creation to db
            inv1, inv2 = invoices[0], invoices[1]
            comp1, comp2 = companies[0], companies[1]
            inv1.company, inv2.company = comp1, comp2
            # do creation of companies to db
            safe_bulk_create(Company, companies)
            safe_bulk_create(Invoice, invoices, refresh_fields=test_data.input['refresh_fields'])
            # check that the objects have been created in db and have a link with each-other
            assert Company.objects.count() == test_data.output['created_comp_nr'], 'Wrong number of companies created!'
            assert Invoice.objects.count() == test_data.output['created_inv_nr'], 'Wrong number of invoices created!'
            assert Invoice.objects.get(id=1).company.id == comp1.id, 'Foreign keys failed to be set!'
        else:
            # creation of simple objects
            safe_bulk_create(Invoice, invoices)
            assert Company.objects.count() == test_data.output['created_comp_nr'], 'Wrong number of companies created!'
            assert Invoice.objects.count() == test_data.output['created_inv_nr'], 'Wrong number of invoices created!'
            assert Invoice.objects.get(id=1).company is None, 'Foreign key should be None!'


@pytest.mark.django_db
@pytest.mark.parametrize('test_data', SAFE_BULK_UPDATE_TEST_CASES)
def test_safe_bulk_update_with_relations(test_data, initial_db_models_with_relations):
    if test_data.output is None:
        assert safe_bulk_update(**test_data.input) is None, 'Function must return None!'

    else:
        old_codes = list(test_data.input['model'].objects.values_list('code', flat=True))
        old_c_names = list(test_data.input['model'].objects.values_list('company__name', flat=True))
        new_comp = Company.objects.create(id=2, name='CN2')
        for rec in test_data.input['records']:
            rec.company = new_comp
        safe_bulk_update(**test_data.input)
        new_codes = list(test_data.input['model'].objects.values_list('code', flat=True))
        new_c_names = list(test_data.input['model'].objects.values_list('company__name', flat=True))

        assert old_codes == test_data.output['old_codes'], 'Codes did not update!'
        assert test_data.output['new_codes'] == new_codes, 'New codes not the right value!'

        assert old_c_names == test_data.output['old_c_names'], 'Company names did not update!'
        assert test_data.output['new_c_names'] == new_c_names, 'New company names not the right value!'


@pytest.mark.django_db
def test_safe_bulk_update_with_no_updated_at_field(initial_db_models_with_relations):
    comp = Company(id=1, name='updated')
    assert Company.objects.first().name != comp.name, 'Update happened without reason!'
    safe_bulk_update(model=Company, records=[comp], fields=['name'])
    assert Company.objects.first().name == 'updated', 'Update did not happen!'
