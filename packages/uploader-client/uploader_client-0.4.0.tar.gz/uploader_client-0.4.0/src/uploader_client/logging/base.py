# coding: utf-8
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import (
    asdict,
)
from datetime import (
    datetime,
)
from typing import (
    TYPE_CHECKING,
    Optional,
)

from django.utils import (
    timezone,
)
from pydantic.fields import (
    Field,
)


if TYPE_CHECKING:
    from dataclasses import \
        dataclass  # noqa
else:
    from pydantic.dataclasses import \
        dataclass  # noqa


@dataclass
class Entry:

    request: str = Field(
        title='Запрос'
    )
    response: Optional[str] = Field(
        title='Ответ на запрос',
        default=None
    )
    error: Optional[str] = Field(
        title='Ошибка',
        default=None
    )
    date_time: datetime = Field(
        default_factory=timezone.now,
        title='Дата и время отправки запроса'
    )

    def __str__(self):
        return (
            '[{date_time}] {request}\n{response}\n{error}'.format(
                **asdict(self)
            )
        )

class AbstractLogger(ABC):
    """Абстрактный логгер."""

    @abstractmethod
    async def log(self, entry) -> None:
        """Логирует сообщение об ошибке."""
        raise NotImplementedError()
