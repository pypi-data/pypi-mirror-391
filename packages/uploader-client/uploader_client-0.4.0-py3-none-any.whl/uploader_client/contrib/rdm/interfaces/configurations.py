from pydantic.fields import (
    Field,
)
from typing import (
    TYPE_CHECKING,
    Optional,
)

from uploader_client.configurations import (
    Config as UploaderConfig,
)
from uploader_client.const import (
    DEFAULT_REQUEST_RETRIES,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_RETRY_FACTOR,
    FILE_STATUS_SUCCESS,
)
from uploader_client.contrib.rdm.interfaces.cache import (
    AbstractRedisCache,
    DEFAULT_CACHE_LOCK_TIMEOUT,
)


if TYPE_CHECKING:
    from dataclasses import (
        dataclass,
    )
else:
    from pydantic.dataclasses import (
        dataclass,
    )


class DataclassConfig:
    """Конфигурация дата-класса pydantic."""

    arbitrary_types_allowed = True


@dataclass(config=DataclassConfig)
class RegionalDataMartUploaderConfig(UploaderConfig):
    """Объект конфигурации загрузчика в витрину данных."""

    url: str = Field(
        title='Адрес витрины данных (schema://host:post)',
        default='http://localhost:8090',
        min_length=1,
    )

    datamart_name: str = Field(
        title='Мнемоника витрины',
        min_length=1,
        default='?',
    )

    cache: Optional[AbstractRedisCache] = Field(
        title='Кеш для возможности хранения токена доступа',
    )

    cache_lock_timeout: int = Field(
        title='Кол-во секунд удержания блокировки доступа к кешу',
        default=DEFAULT_CACHE_LOCK_TIMEOUT,
    )

    organization_ogrn: Optional[str] = Field(
        title='ОГРН организации',
    )

    installation_name: Optional[str] = Field(
        title='Имя инсталляции в целевой Витрине',
    )

    installation_id: Optional[str] = Field(
        title='Идентификатор инсталляции в целевой Витрине',
    )

    username: Optional[str] = Field(
        title='Имя пользователя IAM',
    )

    password: Optional[str] = Field(
        title='Пароль пользователя IAM',
    )

    request_retries: int = Field(
        title='Количество повторных попыток',
        default=DEFAULT_REQUEST_RETRIES,
    )

    retry_factor: int = Field(
        title='Шаг увеличения задержки м.д. запросами',
        default=DEFAULT_RETRY_FACTOR,
    )

    timeout: int = Field(
        title='Таймаут запроса, сек',
        default=DEFAULT_REQUEST_TIMEOUT,
    )

    interface: str = 'uploader_client.interfaces.rest.OpenAPIInterface'

    logger: str = 'uploader_client.logging.db.Logger'


@dataclass(config=DataclassConfig)
class RegionalDataMartEmulationUploaderConfig(RegionalDataMartUploaderConfig):
    """Объект конфигурации загрузчика в витрину данных для тестовых серверов."""

    file_status: str = Field(
        title='Тип ответа от витрины при обработке файла',
        default=FILE_STATUS_SUCCESS,
    )

