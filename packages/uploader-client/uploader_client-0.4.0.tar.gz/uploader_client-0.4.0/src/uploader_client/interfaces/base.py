from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

from pydantic import (
    BaseModel,
)


if TYPE_CHECKING:
    from uploader_client.configurations import (
        Config,
    )
    from uploader_client.logging.base import (
        AbstractLogger,
    )


class AbstractRequest(ABC):
    """Абстрактный запрос."""


class AbstractResult(BaseModel, ABC):
    """Абстрактный результат отправки запроса."""

    class Config:
        arbitrary_types_allowed = True

    request: AbstractRequest
    response: Optional[Any] = None
    error: Optional[str] = None
    log: Optional[Any] = None


class AbstractInterface(ABC):
    """Аcинхронный интерфейс для отправки запросов."""

    _config: 'Config'
    _logger: 'AbstractLogger'

    def __init__(
        self,
        config: 'Config',
        logger: 'AbstractLogger',
    ):
        self._config = config
        self._logger = logger

    @abstractmethod
    async def init(self):
        """Инициализация соединения."""

    @abstractmethod
    async def close(self):
        """Закрытие соединения."""

    @abstractmethod
    async def send(self, request: 'AbstractRequest') -> 'AbstractResult':
        """Отправляет запрос асинхронно, и возвращает результат."""
