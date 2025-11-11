from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.TextField(verbose_name='Запрос')),
                ('response', models.TextField(blank=True, null=True, verbose_name='Ответ на запрос')),
                ('error', models.TextField(blank=True, null=True, verbose_name='Ошибка')),
                ('date_time', models.DateTimeField(verbose_name='Дата и время отправки запроса')),
            ],
            options={
                'verbose_name': 'Журнал запросов',
                'verbose_name_plural': 'Журнал запросов',
                'db_table': 'uploader_client_entry',
            },
        ),
        migrations.AddIndex(
            model_name='entry',
            index=models.Index(fields=['date_time'], name='uploader_cl_date_ti_5c24ec_idx'),
        ),
    ]
