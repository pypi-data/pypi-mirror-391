from unittest import mock

import pytest

from logger_extra.extras.django_auditlog import (
    disable_django_auditlog_augment,
    enable_django_auditlog_augment,
)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    yield
    disable_django_auditlog_augment()


def test_auditlog_present():
    assert enable_django_auditlog_augment()


@mock.patch("logger_extra.extras.django_auditlog.has_auditlog", False)
def test_auditlog_missing():
    assert not enable_django_auditlog_augment()
