import asyncio
import traceback
from abc import (
    abstractmethod,
)
from typing import (
    IO,
    List,
    Optional,
    Tuple,
    Union,
)
from urllib.parse import (
    urljoin,
)

from httpx import (
    Client,
    ConnectError,
    HTTPStatusError,
    Request,
    Response,
)

from uploader_client.const import (
    DEFAULT_REQUEST_TIMEOUT,
)
from uploader_client.interfaces.base import (
    AbstractInterface,
    AbstractRequest,
    AbstractResult,
)
from uploader_client.logging.base import (
    Entry,
)


class AbstractRESTRequest(AbstractRequest):
    """Абстрактный REST-запрос."""


class OpenAPIRequest(AbstractRESTRequest):
    """OpenAPI запрос."""

    @abstractmethod
    def get_url(self) -> str:
        """URL запроса."""

    @abstractmethod
    def get_method(self) -> str:
        """Метод запроса.

        'get', 'post', 'delete', 'patch', 'put' or 'options'.
        """

    def get_params(self) -> dict:
        """Параметры Query string (get)."""
        return {}

    def get_headers(self) -> dict:
        """Заголовки запроса."""
        return {}

    def get_data(self):
        """Тело запроса."""
        return None

    def get_files(self) -> List[Tuple['str', IO]]:
        """Файлы в запросе.

        (
            ('files', Path(name1).open('rb'),
            ('files', Path(name2).open('rb'),
        )
        """
        return []

    def get_timeout(self) -> Union[int, None]:
        """Таймаут запроса, сек."""
        return None


class Result(AbstractResult):
    """Результат отправки OpenAPI запроса."""

    request: AbstractRESTRequest
    http_request: Optional[Request] = None


class OpenAPIInterface(AbstractInterface):
    """Асинхронный режим по спецификации OpenAPI.

    Все запросы выполняются в асинхронном режиме в соответствии с загруженной спецификацией OpenAPI.
    Получение результата осуществляется путем выполнения HTTP-запроса.
    """

    async def init(self):
        """Инициализация соединения. Создание клиента."""
        self.client = Client()

    async def close(self):
        """Инициализация соединения. Закрытие клиента."""
        self.client.close()

    async def send(self, request: OpenAPIRequest) -> Result:
        """Отправляет запрос, и возвращает результат отправки запроса."""
        error = response = None
        method = request.get_method().upper()
        url = self._determine_request_url(request)

        httpx_kwargs = dict(
            headers=request.get_headers(),
            params=request.get_params(),
            data=request.get_data(),
            files=request.get_files(),
        )

        http_request = self.client.build_request(method, url, **httpx_kwargs)

        # Логика повторных попыток
        retries = self._config.request_retries
        backoff_factor = self._config.retry_factor
        attempt = 0
        response = None

        while True:
            try:
                response = await self._send_request(http_request)
                response.raise_for_status()
                break
            except (HTTPStatusError, ConnectError, asyncio.TimeoutError) as err:
                if attempt >= retries:
                    error = self._format_error(err)
                    break

                delay = backoff_factor * (2 ** attempt)
                attempt += 1
                await asyncio.sleep(delay)

        entry = Entry(
            request=self._format_http_request(http_request),
            response=self._format_response(response),
            error=error,
        )

        log = await self._log(entry)

        return Result(
            request=request,
            http_request=http_request,
            response=response,
            error=error,
            log=log,
        )

    async def _log(self, entry: Entry):
        result = await self._logger.log(entry)

        return result

    async def _send_request(
        self,
        request: Request,
    ) -> Response:
        return await self.client.send(request)

    def _determine_request_url(self, request: OpenAPIRequest):
        """Определение URL запроса.

        URL = схема + адрес + path запроса.
        """
        return urljoin(
            self._config.url,
            request.get_url(),
        )

    def _select_timeout(self, request: OpenAPIRequest):
        """Определение таймаута.

        Приоритет таймаутов:
            - из запроса
            - из настройки клиента
            - стандартный
        """
        return (
            request.get_timeout()
            or self._config.timeout
            or DEFAULT_REQUEST_TIMEOUT
        )

    def _format_http_request(
        self,
        http_request: Request,
    ) -> str:
        content = http_request.content if http_request.content else ''
        if isinstance(content, bytes):
            content = content.decode('utf-8')

        return (
            f'[{http_request.method}] {http_request.url}\n\n'
            f'{http_request.headers}\n\n'
            f'{content}'
        )

    def _format_error(self, error: Union[Exception, None]) -> str:
        return f'{str(error)}\n\n{traceback.format_exc()}' if error else ''

    def _format_response(self, response: Union[Response, None]) -> str:
        if response is None:
            return ''
        return f'[{response.status_code}] {response.url}\n\n{response.headers}\n\n{response.text}' if response else ''
