from django.db.models.base import (
    Model,
)
from django.db.models.fields import (
    DateTimeField,
    TextField,
)
from django.db.models.indexes import (
    Index,
)
from uploader_client.logging.base import (
    Entry as EntryModel,
)


class Entry(Model):
    """
    Запись журнала взаимодействия.
    """

    request = TextField(
        verbose_name=EntryModel.request.title
    )

    response = TextField(
        verbose_name=EntryModel.response.title,
        null=True, blank=True
    )

    error = TextField(
        verbose_name=EntryModel.error.title,
        null=True, blank=True
    )

    date_time = DateTimeField(
        verbose_name=EntryModel.date_time.title
    )

    class Meta:
        verbose_name = verbose_name_plural = 'Журнал запросов'
        db_table = 'uploader_client_entry'
        indexes = [
            Index(fields=['date_time']),
        ]
