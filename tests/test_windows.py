from context import crossconfig
import os
import platform
import unittest


@unittest.skipIf(platform.system() != "Windows", "Skipping Windows tests on non-Windows system")
class TestWindows(unittest.TestCase):
    app_name: str
    file_name: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.app_name = f"crossconfig-test"
        cls.file_name = os.urandom(10).hex()
        if os.path.exists(f"{cls.app_name}\\settings.json"):
            os.remove(f"{cls.app_name}\\settings.json")
        if os.path.exists(f"{cls.app_name}"):
            os.rmdir(f"{cls.app_name}")
        if os.path.exists(f"{os.path.expanduser('~')}\\{cls.app_name}\\settings.json"):
            os.remove(f"{os.path.expanduser('~')}\\{cls.app_name}\\settings.json")
        if os.path.exists(f"{os.path.expanduser('~')}\\{cls.app_name}"):
            os.rmdir(f"{os.path.expanduser('~')}\\{cls.app_name}")
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(f"{cls.app_name}\\settings.json"):
            os.remove(f"{cls.app_name}\\settings.json")
        if os.path.exists(f"{cls.app_name}"):
            os.rmdir(f"{cls.app_name}")
        if os.path.exists(f"{os.path.expanduser('~')}\\{cls.app_name}\\settings.json"):
            os.remove(f"{os.path.expanduser('~')}\\{cls.app_name}\\settings.json")
        if os.path.exists(f"{os.path.expanduser('~')}\\{cls.app_name}"):
            os.rmdir(f"{os.path.expanduser('~')}\\{cls.app_name}")
        return super().tearDownClass()

    def test_path(self):
        config = crossconfig.WindowsConfig(self.app_name)
        assert config.path()[-len(self.app_name):] == self.app_name, \
            (config.path()[-len(self.app_name):], self.app_name)
        assert config.path("subdir")[-len(self.app_name) - 7:] == f"{self.app_name}\\subdir", \
            (config.path("subdir")[-len(self.app_name) - 7:], f"{self.app_name}\\subdir")
        assert f"{self.app_name}\\subdir\\{self.file_name}" in config.path(["subdir", self.file_name]), \
            (config.path(["subdir", self.file_name]), f"{self.app_name}\\subdir\\{self.file_name}")

    def test_get_config(self):
        config = crossconfig.get_config(self.app_name, portable=False)
        assert type(config) is crossconfig.WindowsConfig
        config = crossconfig.get_config(self.app_name, portable=True)
        assert type(config) is crossconfig.PortableWindowsConfig

    def test_set_and_get_portable(self):
        val = os.urandom(10).hex()
        config = crossconfig.PortableWindowsConfig(self.app_name)
        assert config.get("test") is None
        config.set("test", val)
        assert config.get("test") == val
        config.unset("test")
        assert config.get("test") is None

    def test_set_and_get_nonportable(self):
        val = os.urandom(10).hex()
        config = crossconfig.WindowsConfig(self.app_name)
        assert config.get("test") is None
        config.set("test", val)
        assert config.get("test") == val
        config.unset("test")
        assert config.get("test") is None

    def test_save_and_load(self):
        val = os.urandom(10).hex()
        config = crossconfig.PortableWindowsConfig(self.app_name)
        config.set("test", val)
        config.save()
        config = crossconfig.PortableWindowsConfig(self.app_name)
        assert config.get("test") is None
        config.load()
        assert config.get("test") == val


if __name__ == "__main__":
    unittest.main()
