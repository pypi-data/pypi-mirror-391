from logger_extra.logger_context import get_logger_context, logger_context


def test_logger_context():
    key1 = "key1"
    value1 = "foo"

    with logger_context({key1: value1}):
        assert {key1: value1} == get_logger_context()

        key2 = "key2"
        value2 = "bar"

        with logger_context({key2: value2}):
            assert {key1: value1, key2: value2} == get_logger_context()

            key3 = "key3"
            value3 = "baz"

            with logger_context({key3: value3}):
                assert {
                    key1: value1,
                    key2: value2,
                    key3: value3,
                } == get_logger_context()

            assert {key1: value1, key2: value2} == get_logger_context()

        assert {key1: value1} == get_logger_context()
