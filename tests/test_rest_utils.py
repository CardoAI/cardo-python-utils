from unittest.mock import patch

from helper_module.rest import get_remote_file_as_namedtempfile
from tests.utils import FakeResponse


def test_get_remote_file_as_namedtempfile():
    """
    Tests get_remote_file_as_namedtempfile() function by mocking the requests.get()
    and the response returned by it using the FakeResponse class.
    """
    with patch('requests.get') as mock_request:
        url = 'http://test.com'
        mock_request.return_value = FakeResponse(content=b'test')
        namedtempfile = get_remote_file_as_namedtempfile(url, '.txt')
        assert namedtempfile is not None, 'No TempFile was created!'
        with namedtempfile as file:
            file.seek(0)
            assert file.read().decode() == 'test', 'File was created with wrong content!'
            assert file.name.split('.')[-1] == 'txt', 'Wrong extension was added to file'
