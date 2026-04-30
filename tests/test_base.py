from context import crossconfig
from pathlib import Path
import unittest
import os


class BaseConfig(crossconfig.BaseConfig):
    def base_path(self) -> Path:
        return Path(f"base--{self.app_name}")


class TestBase(unittest.TestCase):
    app_name: str = "test"

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        settings_path = f"base--{cls.app_name}/settings.json"
        if os.path.exists(settings_path):
            os.remove(settings_path)
        if os.path.exists(f"base--{cls.app_name}"):
            os.rmdir(f"base--{cls.app_name}")
        return super().tearDownClass()

    def test_get_set_unset(self):
        config = BaseConfig(self.app_name)
        assert config.get("test") is None, config.get("test")
        config.set("test", "value")
        assert config.get("test") == "value", config.get("test")
        config.unset("test")
        assert config.get("test") is None, config.get("test")

    def test_subscribe_and_publish(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("custom_event", listener)
        config.publish("custom_event", "test_data")
        assert received == [("custom_event", "test_data")], received

    def test_set_triggers_event(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("set", "foo"), listener)
        config.set("foo", "bar")
        assert received == [(("set", "foo"), "bar")], received

        received.clear()
        config.subscribe(("set", "a", "b", "c"), listener)
        config.set(["a", "b", "c"], 123)
        assert received == [(("set", "a", "b", "c"), 123)], received

    def test_unset_triggers_event(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("unset", "foo"), listener)
        config.unset("foo")
        assert received == [(("unset", "foo"), None)], received

    def test_list_key_unset(self):
        config = BaseConfig(self.app_name)
        config.set(["parent", "child", "value"], 123)
        assert config.get(["parent", "child", "value"]) == 123, config.get(["parent", "child", "value"])
        config.unset(["parent", "child", "value"])
        assert config.get(["parent", "child", "value"]) is None, config.get(["parent", "child", "value"])
        assert isinstance(config.get("parent"), dict), config.get("parent")
        assert isinstance(config.get(["parent", "child"]), dict), config.get(["parent", "child"])

    def test_unset_triggers_event_with_list_key(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("unset", "*"), listener)
        config.set(["parent", "child"], "value")
        received.clear()
        config.unset(["parent", "child"])
        assert received == [(("unset", "parent", "child"), None)], received
        received.clear()
        config.unset(["nonexistent", "path"])
        assert received == [(("unset", "nonexistent", "path"), None)], received

    def test_unsubscribe_removes_listener(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("test_event", listener)
        config.publish("test_event", "data1")
        config.unsubscribe("test_event", listener)
        config.publish("test_event", "data2")
        assert received == [("test_event", "data1")], received

    def test_subscribe_type_guards(self):
        config = BaseConfig(self.app_name)
        listener = lambda *_: ...

        with self.assertRaises(TypeError):
            config.subscribe(123, listener)
        with self.assertRaises(TypeError):
            config.subscribe(b'invalid', listener)
        with self.assertRaises(TypeError):
            config.subscribe(('valid', b'invalid'), listener)
        with self.assertRaises(TypeError):
            config.subscribe(('cannot use ints', 123), listener)
        with self.assertRaises(TypeError):
            config.subscribe({'invalid'}, listener)
        with self.assertRaises(TypeError):
            config.subscribe({'not':'valid'}, listener)
        # str is valid
        config.subscribe('valid', listener)
        with self.assertRaises(TypeError):
            config.subscribe('valid', 'not callable')

        # list[str] and tuple[str] valid
        config.subscribe(('secret', 'compatibility'), listener)
        config.subscribe(['secret', 'compatibility'], listener)

    def test_unsubscribe_type_guards(self):
        config = BaseConfig(self.app_name)
        listener = lambda *_: ...

        with self.assertRaises(TypeError):
            config.unsubscribe(123, listener)
        with self.assertRaises(TypeError):
            config.unsubscribe(b'invalid', listener)
        with self.assertRaises(TypeError):
            config.unsubscribe(('valid', b'invalid'), listener)
        with self.assertRaises(TypeError):
            config.unsubscribe(('cannot use ints', 123), listener)
        with self.assertRaises(TypeError):
            config.unsubscribe({'invalid'}, listener)
        with self.assertRaises(TypeError):
            config.unsubscribe({'not':'valid'}, listener)
        # str is valid
        config.unsubscribe('valid', listener)
        with self.assertRaises(TypeError):
            config.unsubscribe('valid', 'not callable')

        # list[str] and tuple[str] valid
        config.unsubscribe(('secret', 'compatibility'), listener)
        config.unsubscribe(['secret', 'compatibility'], listener)

    def test_duplicate_subscription_prevention(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("test_event", listener)
        config.subscribe("test_event", listener)
        config.publish("test_event", "data")
        assert received == [("test_event", "data")], received

    def test_wildcard_all(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("*", listener)
        config.set("foo", "value1")
        config.set(["nested", "path", "value"], "nested_value")
        config.unset("foo")
        config.publish("custom", "custom_data")
        assert len(received) == 4, len(received)
        assert (("set", "foo"), "value1") in received, received
        assert (("set", "nested", "path", "value"), "nested_value") in received, received
        assert (("unset", "foo"), None) in received, received
        assert ("custom", "custom_data") in received, received

    def test_wildcard_set_star(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("set", "*"), listener)
        config.set("foo", "value1")
        config.set("bar", "value2")
        config.set(["nested", "key"], "nested_value")
        config.unset("foo")
        assert len(received) == 3, len(received)
        assert (("set", "foo"), "value1") in received, received
        assert (("set", "bar"), "value2") in received, received
        assert (("set", "nested", "key"), "nested_value") in received, received

    def test_wildcard_unset_star(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("unset", "*"), listener)
        config.set("foo", "value")
        config.unset("foo")
        config.unset("bar")
        assert len(received) == 2, len(received)
        assert (("unset", "foo"), None) in received, received
        assert (("unset", "bar"), None) in received, received

    def test_wildcard_key_ending(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("*", "foo"), listener)
        config.set("foo", "value1")
        config.set("bar", "value2")
        config.unset("foo")
        config.unset("bar")
        assert len(received) == 2, received
        assert (("set", "foo"), "value1") in received, received
        assert (("unset", "foo"), None) in received, received

    def test_multiple_wildcards_deduplication(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("set", "foo"), listener)
        config.subscribe(("set", "*"), listener)
        config.subscribe("*", listener)
        config.set("foo", "value")
        assert received == [(("set", "foo"), "value")], received

    def test_publishing_with_no_subscribers_raises_no_errors(self):
        config = BaseConfig(self.app_name)
        config.publish("nonexistent", "data")

    def test_unsubscribe_nonexistent_subscribers_raises_no_errors(self):
        config = BaseConfig(self.app_name)
        config.unsubscribe("nonexistent", lambda *_: None)

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
        assert received == [("test_event", "data")], received

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
        assert received1 == [("test_event", "data")], received1
        assert received2 == [("test_event", "data")], received2
        assert received3 == [("test_event", "data")], received3

    def test_custom_publish(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("custom_event", listener)
        config.publish("custom_event", {"key": "value"})
        config.publish("another_event", [1, 2, 3])
        assert len(received) == 1, len(received)
        assert received == [("custom_event", {"key": "value"})], received

    def test_mixed_value_types(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("set", "foo"), listener)
        config.set("foo", "string_value")
        config.set("bar", 42)
        config.set("baz", True)
        config.set("qux", 3.14)
        assert len(received) == 1, len(received)
        assert received == [(("set", "foo"), "string_value")], received

    def test_list_key_single_element(self):
        config = BaseConfig(self.app_name)
        config.set(["simple_key"], "simple_value")
        assert config.get(["simple_key"]) == "simple_value", config.get(["simple_key"])
        assert config.get("simple_key") == "simple_value", config.get("simple_key")

    def test_list_key_nested_structure_creation(self):
        config = BaseConfig(self.app_name)
        config.set(["thing", "does", "not", "exist"], 123)
        assert config.get(["thing", "does", "not", "exist"]) == 123, config.get(["thing", "does", "not", "exist"])
        assert config.settings["thing"]["does"]["not"]["exist"] == 123, config.settings["thing"]["does"]["not"]["exist"]
        assert config.settings["thing"] == {"does": {"not": {"exist": 123}}}, config.settings["thing"]

    def test_list_key_get_with_default(self):
        config = BaseConfig(self.app_name)
        config.set(["exists"], "value")
        assert config.get(["exists", "missing"], "default_val") == "default_val", config.get(["exists", "missing"], "default_val")
        assert config.get(["completely", "missing", "path"], 42) == 42, config.get(["completely", "missing", "path"], 42)

    def test_list_key_overwrite_existing_value(self):
        config = BaseConfig(self.app_name)
        config.set("nested", "key")
        assert config.get("nested") == "key", config.get("nested")
        config.set(["nested", "key"], "original")
        assert config.get("nested") == {"key": "original"}, config.get("nested")
        assert config.get(["nested", "key"]) == "original", config.get(["nested", "key"])
        config.set(["nested", "key"], "updated")
        assert config.get(["nested", "key"]) == "updated", config.get(["nested", "key"])

    def test_list_key_intermediate_dict_preservation(self):
        config = BaseConfig(self.app_name)
        config.set(["path", "to", "value1"], 100)
        config.set(["path", "to", "value2"], 200)
        config.set(["path", "from", "value3"], 300)
        assert config.get(["path", "to", "value1"]) == 100, config.get(["path", "to", "value1"])
        assert config.get(["path", "to", "value2"]) == 200, config.get(["path", "to", "value2"])
        assert config.get(["path", "from", "value3"]) == 300, config.get(["path", "from", "value3"])
        assert config.settings["path"]["to"] == {"value1": 100, "value2": 200}, config.settings["path"]["to"]
        assert config.settings["path"]["from"] == {"value3": 300}, config.settings["path"]["from"]

    def test_save_event_published(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("save", listener)
        config.set("test", "value")
        config.save()
        assert received == [("save", None)], received

    def test_load_event_published_success(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.set("test", "value")
        config.save()
        config2 = BaseConfig(self.app_name)
        config2.subscribe("load", listener)
        config2.load()
        assert len(received) == 1, len(received)
        assert received[0][0] == "load", received[0][0]
        assert received[0][1] == {"test": "value"}, received[0][1]

    def test_load_event_published_no_file(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        settings_path = config.path("settings.json")
        if os.path.exists(settings_path):
            os.remove(settings_path)

        config.subscribe("load", listener)
        config.load()
        assert received == [("load", {})], received

    def test_load_event_published_json_error(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        import json
        config.subscribe("load", listener)
        settings_path = config.path("settings.json")
        with open(settings_path, "w") as f:
            f.write("invalid json {")
        result = config.load()
        assert len(received) == 1, len(received)
        assert received[0][0] == "load", received[0][0]
        assert isinstance(received[0][1], json.decoder.JSONDecodeError), received[0][1]
        assert result is received[0][1], result

    def test_custom_event_bubbling(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("do", "something"), listener)
        config.publish(("do", "something"), "exact")
        config.publish(("do", "something", "more"), "child")
        config.publish(("do", "something", "ad", "nauseum"), "deep_child")
        assert len(received) == 3, len(received)
        assert received[0] == (("do", "something"), "exact"), received[0]
        assert received[1] == (("do", "something", "more"), "child"), received[1]
        assert received[2] == (
            ("do", "something", "ad", "nauseum"), "deep_child"
        ), received[2]

    def test_custom_event_wildcard(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("*", "something"), listener)
        config.publish(("do", "something"), "data1")
        config.publish(("do_not", "something"), "data2")
        config.publish(("whatever", "something", "child", "grandchild"), "data3")
        assert len(received) == 3, len(received)
        assert received[0] == (("do", "something"), "data1"), received[0]
        assert received[1] == (("do_not", "something"), "data2"), received[1]
        assert received[2] == (
            ("whatever", "something", "child", "grandchild"), "data3"
        ), received[2]

    def test_string_publish_fires_tuple_subscription(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe(("custom",), listener)
        config.publish("custom", "data")
        assert received == [("custom", "data")], received

    def test_single_tuple_publish_fires_string_subscription(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("custom", listener)
        config.publish(("custom",), "data")
        assert received == [(("custom",), "data")], received

    def test_nested_tuple_no_string_subscription(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("custom", listener)
        config.publish(("custom", "child"), "data")
        assert len(received) == 0, f"Expected 0 events, got {len(received)}"

    def test_string_tuple_event_deduplication(self):
        config = BaseConfig(self.app_name)
        received = []

        def listener(event, data):
            received.append((event, data))

        config.subscribe("test", listener)
        config.subscribe(("test",), listener)
        config.publish("test", "data")
        assert received == [("test", "data")], received


if __name__ == "__main__":
    unittest.main()
