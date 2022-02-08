import pytest

from python_utils.data_structures import get_differences, Finder
from tests.tests_data_structures.tests_data import GET_DIFFERENCES_TEST_CASES, FINDER_FIND_TEST_CASES, \
    FINDER_FILTER_TEST_CASES


@pytest.mark.parametrize('test_data', GET_DIFFERENCES_TEST_CASES)
def test_get_differences(test_data):
    output = get_differences(**test_data.input)
    assert output == test_data.output, 'Wrong output from function!'


@pytest.mark.parametrize('test_data', FINDER_FIND_TEST_CASES)
def test_finder_find(test_data, initial_objects):
    obj = Finder(initial_objects).find(**test_data.input)
    if test_data.output is None:
        assert obj is None, 'Wrong object returned!'
    else:
        assert test_data.output == obj.text, 'Wrong object returned!'


def test_finder_filter_on_empty_list():
    assert Finder([]).find(id=1) is None, 'Wrong object returned!'


@pytest.mark.parametrize('test_data', FINDER_FILTER_TEST_CASES)
def test_finder_filter(test_data, initial_objects):
    objects = Finder(initial_objects).filter(**test_data.input)
    if 'as_list' in test_data.input:
        assert type(objects) == filter, 'Wrong type returned!'
        assert sum(1 for _ in objects) == 3, 'Wrong number of objects inside filter returned!'
    else:
        assert type(objects) == list, 'Wrong type returned!'
        assert test_data.output == str(objects), 'Wrong objects returned!'
