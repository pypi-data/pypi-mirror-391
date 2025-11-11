from typing import (
    TYPE_CHECKING,
)

from uploader_client.utils import (
    import_string,
)


if TYPE_CHECKING:
    from uploader_client.configurations import (
        Config,
    )
    from uploader_client.interfaces import (
        AbstractInterface,
        AbstractRequest,
        AbstractResult,
    )
    from uploader_client.logging.base import (
        AbstractLogger,
    )


class UploaderAdapter:
    """Адаптер для загрузки файлов."""

    _config: 'Config'
    _interface: 'AbstractInterface'
    _logger: 'AbstractLogger'

    def __init__(self):
        self._config = None
        self._load_config()

    async def init(self):
        """Инициализация соединения."""
        await self._interface.init()

    async def close(self):
        """Закрытие соединения."""
        await self._interface.close()

    def _load_config(self) -> 'Config':
        from uploader_client import (
            get_config,
        )

        set_config = get_config()

        if self._config is not set_config:
            self._config = set_config

        self._logger = import_string(self._config.logger)()
        self._interface = import_string(
            self._config.interface
        )(
            self._config, self._logger
        )

        return self._config

    async def send(self, request: 'AbstractRequest') -> 'AbstractResult':
        """Отправка запроса."""
        return await self._interface.send(request)
