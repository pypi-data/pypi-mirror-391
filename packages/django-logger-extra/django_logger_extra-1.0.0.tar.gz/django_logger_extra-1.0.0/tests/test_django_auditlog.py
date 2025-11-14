import uuid

import pytest
from auditlog.models import LogEntry

from logger_extra.extras.django_auditlog import (
    disable_django_auditlog_augment,
    enable_django_auditlog_augment,
)
from logger_extra.logger_context import logger_context
from tests.models import DummyModel


@pytest.fixture(autouse=True)
def setup_and_teardown():
    enable_django_auditlog_augment()
    yield
    disable_django_auditlog_augment()


@pytest.mark.django_db
def test_auditlog_augment():
    instance: DummyModel
    expected1 = str(uuid.uuid4())
    expected2 = str(uuid.uuid4())
    expected3 = str(uuid.uuid4())

    with logger_context({"value1": expected1}):
        with logger_context({"value2": expected2}):
            with logger_context({"value3": expected3}):
                instance = DummyModel.objects.create(message="Hello")

    audit_log_instance = LogEntry.objects.get(object_pk=instance.id)
    assert audit_log_instance is not None

    additional_data = audit_log_instance.additional_data
    assert additional_data.get("value1", None) == expected1
    assert additional_data.get("value2", None) == expected2
    assert additional_data.get("value3", None) == expected3
