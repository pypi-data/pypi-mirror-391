import cgi
import csv
import io
import re
from functools import (
    partial,
)
from typing import (
    TYPE_CHECKING,
)

from requests import (
    Request,
)


if TYPE_CHECKING:
    from httpx import (
        Request as HttpxRequest,
    )
    from requests import (
        PreparedRequest,
    )


def join_parts(parts, delimiter=';'):
    return delimiter.join(parts)


join_lines = partial(join_parts, delimiter='\n')


def try_decode_csv(value) -> str:
    """Проверка возможности декодирования csv."""

    delimiter_ = ';'

    if issubclass(type(value), bytes):
        value = value.decode('utf-8')

    reader = csv.reader(io.StringIO(value), delimiter=delimiter_)

    result = join_lines(
        join_parts(parts) for parts in reader
    )
    return result


def try_decode_multipart(value):
    boundary = re.compile(
        '(--){1}([a-z1-90]{32})(\\r\\n).*'
    ).match(
        value.decode('utf-8')
    )[2]

    result = cgi.parse_multipart(
        io.BytesIO(value),
        {
            'boundary': boundary.encode('ASCII')
        }
    )
    return result


def convert_httpx_to_prepared_request(httpx_request: 'HttpxRequest') -> 'PreparedRequest':
    """Создает и подготавливает объект requests.PreparedRequest, заполненный данными из httpx.Request.

    Необходим, поскольку OpenAPI не поддерживает асинхронный httpx
    """
    method = httpx_request.method
    url = str(httpx_request.url)
    headers = dict(httpx_request.headers)
    body = httpx_request.content

    request = Request(
        method=method,
        url=url,
        headers=headers,
        data=body,
    )
    prepared_request = request.prepare()

    return prepared_request
