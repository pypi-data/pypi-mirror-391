import fnmatch
from itertools import (
    chain,
)
from openapi_core.templating.media_types.exceptions import (
    MediaTypeNotFound,
)
from openapi_core.templating.media_types.finders import (
    MediaTypeFinder as BaseMediaTypeFinder,
)
from openapi_core.validation.request.validators import (
    RequestValidator as BaseRequestValidator,
)
from uploader_client.contrib.rdm.interfaces import (
    utils,
)
from openapi_core.validation.exceptions import (
    InvalidSecurity,
)
from openapi_core.validation.request.datatypes import (
    RequestValidationResult,
)
from openapi_core.templating.paths.exceptions import (
    PathError,
)


class MediaTypeFinder(BaseMediaTypeFinder):
    def find(self, request):
        if request.mimetype in self.content:
            return self.content / request.mimetype, request.mimetype

        for key, value in self.content.items():
            if (
                key in request.mimetype or
                fnmatch.fnmatch(request.mimetype, key)
            ):
                return value, key

        raise MediaTypeNotFound(request.mimetype, list(self.content.keys()))


class RequestValidator(BaseRequestValidator):
    media_type_finder_cls = MediaTypeFinder

    def __init__(
        self, *args, custom_media_type_deserializers=None, **kwargs
    ):
        custom_media_type_deserializers: dict = custom_media_type_deserializers or {}
        custom_media_type_deserializers.update({
            'text/csv': utils.try_decode_csv,
            'multipart/form-data': utils.try_decode_multipart
        })
        super().__init__(
            *args, custom_media_type_deserializers=custom_media_type_deserializers
        )

    def _get_media_type(self, content, request_or_response):
        return self.media_type_finder_cls(content).find(request_or_response)

    def validate(self, request):
        try:
            path, operation, _, path_result, _ = self._find_path(request)
        except PathError as exc:
            return RequestValidationResult(errors=[exc, ])

        try:
            security = self._get_security(request, operation)
        except InvalidSecurity as exc:
            return RequestValidationResult(errors=[exc, ])

        request.parameters.path = request.parameters.path or path_result.variables

        operation_params = operation.get('parameters', [])
        operation_params_iter = operation_params and iter(operation_params) or []

        path_params = path.get('parameters', [])
        params_params_iter = path_params and iter(path_params) or []

        params, params_errors = self._get_parameters(
            request, chain(
                operation_params_iter,
                params_params_iter,
            )
        )

        body, body_errors = self._get_body(request, operation)

        errors = params_errors + body_errors

        return RequestValidationResult(
            errors=errors,
            body=body,
            parameters=params,
            security=security,
            path=path_result,
        )
