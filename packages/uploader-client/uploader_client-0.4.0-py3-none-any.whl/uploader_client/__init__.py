from typing import (
    Union,
)

from uploader_client.configurations import (
    AbstractConfig,
)


__config: Union[AbstractConfig, None] = None


def set_config(config: AbstractConfig):
    """Установка объекта конфигурации пакета."""

    global __config

    assert isinstance(config, AbstractConfig)

    __config = config


def get_config() -> AbstractConfig:
    """Получение установленного объекта конфигурации."""

    global __config

    assert isinstance(__config, AbstractConfig), 'Не произведена настройка клиента'

    return __config
