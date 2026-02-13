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


if __name__ == "__main__":
    unittest.main()
