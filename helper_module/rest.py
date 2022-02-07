from urllib.parse import urlencode

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, \
    HTTP_502_BAD_GATEWAY


def bad_request(message="Bad request."):  # pragma no cover
    return Response(data={"message": message}, status=HTTP_400_BAD_REQUEST)


def unauthorized(message="Unauthorized."):  # pragma no cover
    return Response(data={"message": message}, status=HTTP_401_UNAUTHORIZED)


def forbidden(message="Forbidden."):  # pragma no cover
    return Response(data={"message": message}, status=HTTP_403_FORBIDDEN)


def bad_gateway(message="Bad Gateway."):  # pragma no cover
    return Response(data={"message": message}, status=HTTP_502_BAD_GATEWAY)


def add_params_to_url(url: str, **kwargs) -> str:
    """
    Join the url and params ready for making requests

    Args:
        url: string representing the url to be called
        **kwargs: all the params to join the url
    Returns:
        Final url ready for request
    Examples:
        >>> add_params_to_url('https://test.com', p1='20', p2=30, p3=None, p4='test', p5='<html/>')
        'https://test.com?p1=20&p2=30&p3=None&p4=test&p5=%3Chtml%2F%3E'
    """
    return url if not kwargs else f"{url}?{urlencode(kwargs)}"


def get_remote_file_as_namedtempfile(file_url: str, extension: str = None):
    """
    Reads a remote file from the url. Creates a temporary file, available to be used
    for libraries / functionalities that are unable to process remote files

    Args:
        file_url: string url to get the file from
        extension: string to be added to the end of the file created
    Returns:
        NamedTemporaryFile with the contents of the file from url
    """
    import tempfile, requests
    namedtempfile = tempfile.NamedTemporaryFile()
    namedtempfile.name = f'{namedtempfile.name}{extension}'
    namedtempfile.write(requests.get(file_url).content)
    return namedtempfile
