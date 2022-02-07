import pytest

from python_utils.data_structures import Finder
from tests.tests_finder.tests_data import FIND_TEST_CASES, FILTER_TEST_CASES


@pytest.mark.parametrize('test_data', FIND_TEST_CASES)
def test_find(test_data, initial_objects):
    obj = Finder(initial_objects).find(**test_data.input)
    if test_data.output is None:
        assert obj is None, 'Wrong object returned!'
    else:
        assert test_data.output == obj.text, 'Wrong object returned!'


def test_filter_on_empty_list():
    assert Finder([]).find(id=1) is None, 'Wrong object returned!'


@pytest.mark.parametrize('test_data', FILTER_TEST_CASES)
def test_filter(test_data, initial_objects):
    objects = Finder(initial_objects).filter(**test_data.input)
    if 'as_list' in test_data.input:
        assert type(objects) == filter, 'Wrong type returned!'
        assert sum(1 for _ in objects) == 3, 'Wrong number of objects inside filter returned!'
    else:
        assert type(objects) == list, 'Wrong type returned!'
        assert test_data.output == str(objects), 'Wrong objects returned!'
