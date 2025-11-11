import json
import logging
from json import (
    JSONDecodeError,
    load,
)
from pathlib import (
    Path,
)
from typing import (
    TYPE_CHECKING,
    Optional,
    Tuple,
    Union,
)

from httpx import (
    Response,
)
from openapi_core.contrib.requests import (
    RequestsOpenAPIRequest,
)
from openapi_core.spec.shortcuts import (
    create_spec,
)
from pydantic.dataclasses import (
    dataclass,
)

from uploader_client.const import (
    DEFAULT_REQUEST_TIMEOUT,
    FILE_STATUS_SUCCESS,
)
from uploader_client.contrib.rdm.interfaces.utils import (
    convert_httpx_to_prepared_request,
)
from uploader_client.contrib.rdm.interfaces.validation import (
    RequestValidator,
)
from uploader_client.interfaces.rest import (
    OpenAPIInterface,
    OpenAPIRequest,
)


if TYPE_CHECKING:
    from httpx import (
        Request,
    )

    from uploader_client.contrib.rdm.interfaces.configurations import (
        RegionalDataMartUploaderConfig,
    )
    from uploader_client.interfaces.rest import (
        Result,
    )


logger = logging.getLogger('uploader_client')


@dataclass
class ProxyAPITokenRequest(OpenAPIRequest):
    """Запрос на получение токена Proxy API."""

    username: str
    password: str
    organization_ogrn: str
    datamart_name: str
    timeout: int = DEFAULT_REQUEST_TIMEOUT

    def get_method(self) -> str:
        """Метод запроса."""
        return 'POST'

    def get_url(self) -> str:
        """URL запроса."""
        return f'/api/v1/auth_system'

    def get_data(self) -> dict:
        """Возвращает содержимое запроса."""
        return {
            'username': self.username,
            'password': self.password,
            'organization_ogrn': self.organization_ogrn,
            'datamart_memonic': self.datamart_name,
        }

    def get_timeout(self) -> int:
        """Возвращает время ожидания ответа."""
        return self.timeout


class DataclassConfig:
    """Конфигурация дата-класса pydantic."""

    arbitrary_types_allowed = True


@dataclass(config=DataclassConfig)
class ProxyAPIRequest(OpenAPIRequest):
    """Запрос через Proxy API.

    В качестве параметра принимает исходный запрос, который будет отправлен через Proxy API.
    """

    request: OpenAPIRequest
    organization_ogrn: str
    datamart_name: str
    installation_name: str
    installation_id: int
    access_token: str

    def get_method(self) -> str:
        """Получение метода запроса."""
        return self.request.get_method()

    def get_url(self) -> str:
        """Получение сформированного URL."""
        request_url = self.request.get_url()
        proxy_url = (
            f'/api/v1/secure/'
            f'{self.organization_ogrn}/{self.datamart_name}/{self.installation_name}/{self.installation_id}/'
        )

        return f'{proxy_url}{request_url.lstrip("/")}'

    def get_headers(self) -> dict:
        """Возвращает заголовки запроса."""
        headers = self.request.get_headers()
        headers.update({
            'Authorization': f'Bearer {self.access_token}'
        })

        return headers

    def get_files(self) -> list:
        """Возвращает файлы для отправки."""
        return self.request.get_files()

    def get_data(self) -> Optional[dict]:
        """Возвращает содержимое запроса."""
        return self.request.get_data()

    def get_timeout(self) -> Optional[int]:
        """Возвращает время ожидания ответа."""
        return self.request.get_timeout()


class ProxyAPIInterface(OpenAPIInterface):
    """Интерфейс взаимодействия с РВД через Proxy API."""

    _config: 'RegionalDataMartUploaderConfig'
    ACCESS_TOKEN_CACHE_KEY = 'rdm:uploader_client:access_token'  # noqa: S105

    def _get_token_request(self) -> ProxyAPITokenRequest:
        """Возвращает запрос на получение токена."""
        return ProxyAPITokenRequest(
            datamart_name=self._config.datamart_name,
            username=self._config.username,
            password=self._config.password,
            organization_ogrn=self._config.organization_ogrn,
            timeout=self._config.timeout,
        )

    async def _fetch_access_token(self) -> Tuple[Optional[str], Optional['Result']]:
        """Возвращает токен доступа, либо ответ с ошибкой."""
        access_token = self._config.cache.get(self.ACCESS_TOKEN_CACHE_KEY)

        if not access_token:
            with self._config.cache.lock(
                f'{self.ACCESS_TOKEN_CACHE_KEY}:lock',
                timeout=self._config.cache_lock_timeout,
            ):
                access_token = self._config.cache.get(self.ACCESS_TOKEN_CACHE_KEY)
                if not access_token:
                    result = await self.send(self._get_token_request(), use_proxy=False)
                    if result.error:
                        return None, result

                    try:
                        response_data = result.response.json()
                        access_token = response_data['access_token']
                        expires_in = response_data['expires_in']
                    except (KeyError, TypeError, JSONDecodeError) as err:
                        result.error = self._format_error(err)
                        return None, result

                    if not (access_token and expires_in):
                        result.error = 'В ответе отсутствует токен, либо время действия токена!'
                        return None, result

                    self._config.cache.set(self.ACCESS_TOKEN_CACHE_KEY, access_token, expires_in)

        return access_token, None

    async def _send_through_proxy(self, request: ProxyAPIRequest) -> 'Result':
        """Отправка запроса через Proxy API."""
        access_token, error_result = await self._fetch_access_token()
        if error_result:
            return error_result

        proxy_request = ProxyAPIRequest(
            request=request,
            datamart_name=self._config.datamart_name,
            organization_ogrn=self._config.organization_ogrn,
            installation_name=self._config.installation_name,
            installation_id=self._config.installation_id,
            access_token=access_token,
        )

        return await self.send(proxy_request, use_proxy=False)

    async def send(self, request: ProxyAPIRequest, use_proxy: bool = True) -> 'Result':
        """Отправляет запрос, и возвращает результат отправки запроса."""
        if use_proxy:
            return await self._send_through_proxy(request)

        return await super().send(request)


class OpenAPIInterfaceEmulation(OpenAPIInterface):
    """Эмуляция асинхронных запросов."""

    def _get_response_data(
        self,
        path_pattern: str,
        method_name: str,
    ) -> Union[dict, str]:
        """Возвращает ответ запроса по внутреннему файлу (эмуляция ответа)."""
        spec_dict = self._get_spec()

        operation_id = spec_dict['paths'][path_pattern][method_name]['operationId']
        if operation_id == 'status':
            file_status = getattr(self._config, 'file_status', FILE_STATUS_SUCCESS)
            response_data = (
                spec_dict['paths'][path_pattern][method_name]['responses']['200']['content'][
                    'application/json']['schema']['example'][file_status]
            )

        else:
            response_data = (
                spec_dict['paths'][path_pattern][method_name]['responses']['200']['content'][
                    'application/json']['schema']['example']
            )

        return response_data

    async def _send_request(
        self,
        http_request: 'Request',
    ) -> Response:
        """Эмуляция запроса-ответа.

        Получает запрос, вместо отправки валидирует его.
        Код ответа зависит от успешности валидации.
        """
        prepared_request = convert_httpx_to_prepared_request(http_request)
        openapi_request = RequestsOpenAPIRequest(prepared_request)
        validator = self._get_request_validator()

        result = validator.validate(openapi_request)

        content = None

        if result.errors:
            logger.error('; '.join(str(err) for err in result.errors))
            status_code = 400
        else:
            logger.info('Запрос прошел валидацию')
            status_code = 200
            data = self._get_response_data(result.path.pattern, http_request.method.lower())
            if isinstance(data, str):
                content = data.encode()
            else:
                content = json.dumps(data).encode()

        return Response(
            status_code=status_code,
            content=content,
            request=http_request,
        )

    def _get_spec(self):
        """Получения объекта json-спецификации."""
        with Path(__file__).parent.joinpath('rdm.json').open('r') as spec_file:
            return load(spec_file)

    def _get_request_validator(self):
        """Получение валидатора запроса в витрину."""
        spec_dict = self._get_spec()
        return RequestValidator(create_spec(spec_dict))
