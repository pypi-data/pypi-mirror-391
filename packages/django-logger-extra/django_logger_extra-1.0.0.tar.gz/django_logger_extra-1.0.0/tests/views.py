import logging

from django.http import HttpResponse, JsonResponse

from logger_extra.logger_context import logger_context

logger = logging.getLogger(__name__)


def nop(*_, **__):
    return HttpResponse()


def hello(*_, **__):
    """Generate a log entry."""
    logger.info("Hello, world!")
    return HttpResponse("Hello, world!")


def parrot(request, **__):
    """
    Generate a log entry with context taken from query parameters.

    E.g. /parrot?q=123&foo=bar adds {"q": "123", "foo": "bar"} in context.
    """
    with logger_context(request.GET.dict()):
        logger.info("Polly wants a cookie!")
    return JsonResponse(request.GET)


def error(*_, **__):
    raise ValueError("Oh no!")
