# coding: utf-8

from dataclasses import (
    asdict,
)
from typing import (
    Optional,
)

from asgiref.sync import (
    sync_to_async,
)

from ..models import (
    Entry as DBEntry,
)
from .base import (
    AbstractLogger,
    Entry,
)


class Logger(AbstractLogger):
    """Асинхронный логгер."""

    async def log(self, entry: Entry) -> Optional[DBEntry]:
        """Асинхронное логгирование."""
        assert isinstance(entry, Entry)

        db_entry = await sync_to_async(DBEntry.objects.create)(**asdict(entry))

        return db_entry
