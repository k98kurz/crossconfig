from context import crossconfig
import unittest
import os


class BaseConfig(crossconfig.BaseConfig):
    def base_path(self) -> str:
        return f"base--{self.app_name}"


class TestBase(unittest.TestCase):
    app_name: str = "test"

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(f"base--{cls.app_name}"):
            os.rmdir(f"base--{cls.app_name}")
        return super().tearDownClass()

    def test_get_set_unset(self):
        config = BaseConfig(self.app_name)
        assert config.get("test") is None
        config.set("test", "value")
        assert config.get("test") == "value"
        config.unset("test")
        assert config.get("test") is None

    def test_subscribe_and_publish(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("custom_event", listener)
        config.publish("custom_event", "test_data")
        assert received == [("custom_event", "test_data")]

    def test_set_triggers_event(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("set_foo", listener)
        config.set("foo", "bar")
        assert received == [("set_foo", "bar")]

    def test_unset_triggers_event(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("unset_foo", listener)
        config.unset("foo")
        assert received == [("unset_foo", None)]

    def test_unsubscribe_removes_listener(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("test_event", listener)
        config.publish("test_event", "data1")
        config.unsubscribe("test_event", listener)
        config.publish("test_event", "data2")
        assert received == [("test_event", "data1")]

    def test_duplicate_subscription_prevention(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("test_event", listener)
        config.subscribe("test_event", listener)
        config.publish("test_event", "data")
        assert received == [("test_event", "data")]

    def test_wildcard_all(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("*", listener)
        config.set("foo", "value1")
        config.unset("foo")
        config.publish("custom", "custom_data")
        assert len(received) == 3
        assert ("set_foo", "value1") in received
        assert ("unset_foo", None) in received
        assert ("custom", "custom_data") in received

    def test_wildcard_set_star(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("set_*", listener)
        config.set("foo", "value1")
        config.set("bar", "value2")
        config.unset("foo")
        assert len(received) == 2
        assert ("set_foo", "value1") in received
        assert ("set_bar", "value2") in received

    def test_wildcard_unset_star(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("unset_*", listener)
        config.set("foo", "value")
        config.unset("foo")
        config.unset("bar")
        assert len(received) == 2
        assert ("unset_foo", None) in received
        assert ("unset_bar", None) in received

    def test_wildcard_key_ending(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("*_foo", listener)
        config.set("foo", "value1")
        config.set("bar", "value2")
        config.unset("foo")
        config.unset("bar")
        assert len(received) == 2
        assert ("set_foo", "value1") in received
        assert ("unset_foo", None) in received

    def test_multiple_wildcards_deduplication(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("set_foo", listener)
        config.subscribe("set_*", listener)
        config.subscribe("*", listener)
        config.set("foo", "value")
        assert received == [("set_foo", "value")]

    def test_no_subscribers_silent(self):
        config = BaseConfig(self.app_name)
        config.publish("nonexistent", "data")
        config.set("test", "value")
        config.unset("test")

    def test_unsubscribe_nonexistent_silent(self):
        config = BaseConfig(self.app_name)

        def listener(event, data):
            pass

        config.unsubscribe("nonexistent", listener)
        config.publish("nonexistent", "data")

    def test_listener_exception_handling(self):
        config = BaseConfig(self.app_name)
        received = []

        def bad_listener(event, data):
            raise RuntimeError("Test error")

        def good_listener(event, data):
            received.append((event, data))

        config.subscribe("test_event", bad_listener)
        config.subscribe("test_event", good_listener)
        config.publish("test_event", "data")
        assert received == [("test_event", "data")]

    def test_multiple_listeners_same_event(self):
        config = BaseConfig(self.app_name)
        received1 = []
        received2 = []
        received3 = []

        def listener1(event, data):
            received1.append((event, data))

        def listener2(event, data):
            received2.append((event, data))

        def listener3(event, data):
            received3.append((event, data))

        config.subscribe("test_event", listener1)
        config.subscribe("test_event", listener2)
        config.subscribe("test_event", listener3)
        config.publish("test_event", "data")
        assert received1 == [("test_event", "data")]
        assert received2 == [("test_event", "data")]
        assert received3 == [("test_event", "data")]

    def test_custom_publish(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("custom_event", listener)
        config.publish("custom_event", {"key": "value"})
        config.publish("another_event", [1, 2, 3])
        assert len(received) == 1
        assert received == [("custom_event", {"key": "value"})]

    def test_event_and_data_format(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            assert isinstance(event, str)
            assert isinstance(data, str)
            received.append((event, data))

        config.subscribe("test_event", listener)
        config.publish("test_event", "test_data")
        assert len(received) == 1

    def test_mixed_value_types(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("set_foo", listener)
        config.set("foo", "string_value")
        config.set("bar", 42)
        config.set("baz", True)
        config.set("qux", 3.14)
        assert len(received) == 1
        assert received == [("set_foo", "string_value")]


if __name__ == "__main__":
    unittest.main()
