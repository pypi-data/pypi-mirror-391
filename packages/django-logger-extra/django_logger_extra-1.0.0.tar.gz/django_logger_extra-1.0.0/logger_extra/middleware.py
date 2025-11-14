import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from logger_extra.logger_context import logger_context

GetResponseFn = Callable[[HttpRequest], HttpResponse]


class RequestIdMiddlewareBase:
    request_header: str
    response_header: str
    get_response: GetResponseFn

    def __init__(
        self,
        request_header: str,
        response_header: str,
        get_response: GetResponseFn,
    ):
        self.request_header = request_header
        self.response_header = response_header
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # Get request id from source header or generate one here.
        request_id = request.headers.get(self.request_header, uuid.uuid4())

        with logger_context({"request_id": request_id}):
            response = self.get_response(request)
            response[self.response_header] = request_id

        return response


class XRequestIdMiddleware(RequestIdMiddlewareBase):
    header_name = "X-Request-ID"

    def __init__(self, get_response):
        super().__init__(self.header_name, self.header_name, get_response)
