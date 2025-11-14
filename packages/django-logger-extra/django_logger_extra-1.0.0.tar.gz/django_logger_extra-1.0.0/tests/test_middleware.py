import logging

import pytest

from logger_extra.filter import LoggerContextFilter


@pytest.fixture(scope="module", autouse=True)
def setup_dummy_middleware_logger():
    logger = logging.getLogger("dummy_middleware")
    logger.addFilter(LoggerContextFilter())
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)


def dummy_middleware(get_response):
    logger = logging.getLogger("dummy_middleware")

    def middleware(request):
        logger.info("dummy_middleware says hi")
        response = get_response(request)
        return response

    return middleware


def test_add_context_to_middleware_logs(caplog, client, settings):
    settings.MIDDLEWARE = [
        "logger_extra.middleware.XRequestIdMiddleware",
        "tests.test_middleware.dummy_middleware",
    ]

    client.get("/nop")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.name == "dummy_middleware"
    assert record.request_id


def test_generate_request_id_if_not_set(caplog, client, settings):
    settings.MIDDLEWARE = [
        "logger_extra.middleware.XRequestIdMiddleware",
    ]

    client.get("/hello")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.request_id


def test_use_request_id_from_header(caplog, client, settings):
    settings.MIDDLEWARE = [
        "logger_extra.middleware.XRequestIdMiddleware",
    ]

    client.get("/hello", headers={"X-Request-ID": "foo"})

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.request_id == "foo"


def test_add_logger_context_in_log_record(caplog, client, settings):
    settings.MIDDLEWARE = [
        "logger_extra.middleware.XRequestIdMiddleware",
    ]

    client.get("/parrot", {"foo": "bar"})

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.request_id
    assert record.foo == "bar"


def test_logger_context_ignores_builtins(caplog, client, settings):
    settings.MIDDLEWARE = [
        "logger_extra.middleware.XRequestIdMiddleware",
    ]

    client.get("/parrot", {"message": "overridden"})

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.request_id
    assert record.message != "overridden"


def test_request_id_is_logged_on_error(caplog, client, settings):
    settings.MIDDLEWARE = [
        "logger_extra.middleware.XRequestIdMiddleware",
    ]

    with pytest.raises(ValueError):
        client.get("/error", headers={"X-Request-ID": "foo"})

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.request_id == "foo"
