"""
File operation module.

Overview:
    This module is used for file operations.

Note:
    This module consists of modules that can be imported in Maya.

Classes:
    ConfigLoader: Load config file.

Functions:
    get_url: Get the server side url.
    get_port_number: Get the port number for conncting maya.
    get_python_dir: Get the directory for output python file.
    get_result_dir: Get the directory for output result file.

"""

import configparser
import os
from logging import getLogger
from typing import Any

logger = getLogger(__name__)


class ConfigLoader:
    def __init__(self, config_file: str = 'config.ini'):
        """Initialize.

        Args:
            config_file (str, optional): The config file. Defaults to 'config.ini'.

        """
        # Get config file path
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file_path = os.path.join(package_dir, config_file)
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Missing config file: {config_file_path}")

        # Read config file
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

        logger.debug(f'Get config: {config_file_path}')

    def get(self, section, option) -> Any:
        """Get the value of the option.

        Args:
            section (str): The section name.
            option (str): The option name.

        Raises:
            KeyError: The section or option does not exist.

        Returns:
            Any: The value of the option.

        """
        if not self.config.has_section(section):
            raise KeyError(f"Missing '{section}' section")
        if not self.config.has_option(section, option):
            raise KeyError(f"Missing '{option}' key in '{section}' section")

        return self.config.get(section, option)

    def get_url(self) -> str:
        """Get the server side url."""
        return self.get('server_settings', 'url')

    def get_port_number(self) -> str:
        """Get the port number for conncting maya."""
        return self.get('server_settings', 'maya_port')

    def get_python_dir(self) -> str:
        """Get the directory for output python file."""
        return self.get('directory', 'python')

    def get_result_dir(self) -> str:
        """Get the directory for output result file."""
        return self.get('directory', 'result')


def get_url() -> str:
    """Get the server side url."""
    return ConfigLoader().get_url()


def get_port_number() -> str:
    """Get the port number for conncting maya."""
    return ConfigLoader().get_port_number()


def get_python_dir() -> str:
    """Get the directory for output python file."""
    file_path = ConfigLoader().get_python_dir()

    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
        logger.debug(f'Make output python directory: {file_path}')

    return file_path


def get_result_dir() -> str:
    """Get the directory for output result file."""
    file_path = ConfigLoader().get_result_dir()

    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
        logger.debug(f'Make output result directory: {file_path}')

    return file_path
