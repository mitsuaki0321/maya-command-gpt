from mayacommandgpt.app.config_operation import ConfigLoader


# Test ConfigLoader class
def test_config_loader_get_url():
    config_loader = ConfigLoader()
    assert config_loader.get_url() == "http://example.com"


def test_config_loader_get_port_number():
    config_loader = ConfigLoader()
    assert config_loader.get_port_number() == '7001'


def test_config_loader_get_python_dir():
    config_loader = ConfigLoader()
    assert config_loader.get_python_dir() == r"D:\commands"


def test_config_loader_get_result_dir():
    config_loader = ConfigLoader()
    assert config_loader.get_result_dir() == r"D:\commands\result"
