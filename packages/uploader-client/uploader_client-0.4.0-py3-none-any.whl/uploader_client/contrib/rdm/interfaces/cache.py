from abc import (
    ABCMeta,
    abstractmethod,
)

DEFAULT_CACHE_LOCK_TIMEOUT = 300  # Кол-во секунд удержания блокировки доступа к кешу


class AbstractRedisCache(metaclass=ABCMeta):
    """Абстрактный интерфейс для аннотации типа с полем кеша конфигурации адаптера."""

    @abstractmethod
    def get(self, key, default=None, **kwargs):
        """Возвращает значение из кеша по ключу."""

    @abstractmethod
    def set(self, key, value, timeout=None, **kwargs):
        """Сохраняет значение в кеш по ключу."""

    @abstractmethod
    def lock(self, name, timeout=None, **kwargs):
        """Захватывает блокировку."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not all((hasattr(v, 'get'), hasattr(v, 'set'), hasattr(v, 'lock'))):
            raise ValueError('instance of RedisCache expected')

        return v
