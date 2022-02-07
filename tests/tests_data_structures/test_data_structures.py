import pytest

from helper_module.data_structures import get_differences
from tests.tests_data_structures.tests_data import GET_DIFFERENCES_TEST_CASES


@pytest.mark.parametrize('test_data', GET_DIFFERENCES_TEST_CASES)
def test_get_differences(test_data):
    output = get_differences(**test_data.input)
    assert output == test_data.output, 'Wrong output from function!'
