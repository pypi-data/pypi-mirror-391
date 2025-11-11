# Клиент для взаимодействия с РВД посредством Адаптера
## Подключение
settings:

    INSTALLED_APPS = [
        'uploader_client',
    ]


apps:

    from django.apps import AppConfig as AppConfigBase

    class AppConfig(AppConfigBase):
    
        name = __package__
    
        def __setup_uploader_client(self):
            import uploader_client
    
            uploader_client.set_config(
                uploader_client.configuration.Config(
                    agent_url='http://localhost:8090',
                    system_mnemonics='MNSV03',
                    timeout=1,
                    request_retries=1,
                )
            )
    
        def ready(self):
            super().ready()
            self.__setup_uploader_client()

## Использование Proxy API для отправки запросов в РВД
Заменить используемый интерфейс на ProxyAPIInterface и добавить необходимые параметры в конфигурации:

    uploader_client.set_config(
        ...,
        RegionalDataMartUploaderConfig(
            interface='uploader_client.contrib.rdm.interfaces.rest.ProxyAPIInterface',
            cache=<cache>,
            url=<url>,
            datamart_name=<datamart_name>,
            organization_ogrn=<organization_ogrn>,
            installation_name=<installation_name>,
            installation_id=<installation_id>,
            username=<username>,
            password=<username>,
        )
    )
где
- cache - кеш django для хранения токена доступа (например, `caches[DEFAULT_CACHE_ALIAS]`);
- url - URL до хоста Datamart Studio;
- datamart_name - мнемоника Витрины;
- organization_ogrn - ОГРН организации, в рамках которой развёрнута Витрина;
- installation_name - имя инсталляции в целевой Витрине;
- installation_id - идентификатор инсталляции;
- username - имя пользователя IAM;
- password - пароль пользователя IAM.
 

## Эмуляция
Заменить используемый интерфейс на эмулирующий запросы:

    uploader_client.set_config(
        ...,
        uploader_client.configuration.Config(
            interface=(
                'uploader_client.contrib.rdm.interfaces.rest'
                '.OpenAPIInterfaceEmulation'
            )
        )
    )

## Запуск тестов
    $ tox

## API

### Передача сообщения

    from uploader_client.adapters import adapter
    from uploader_client.interfaces import OpenAPIRequest

    class Request(OpenAPIRequest):

        def get_url(self):
            return 'http://localhost:8090/MNSV03/myedu/api/edu-upload/v1/multipart/csv'
    
        def get_method(self):
            return 'post'
    
        def get_files(self) -> List[str]:
            return [
                Path('files/myedu_schools.csv').as_posix()
            ]

    result = adapter.send(Request())
