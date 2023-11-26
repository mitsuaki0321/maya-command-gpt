"""
Send command to Maya and get response.

Overview:
    This module is used for sending commands to Maya.

Functions:
    send_python_command: Send to Maya python command.
    get_json_data: Get json data from file.

"""


import json
import os
import socket
from logging import getLogger

from . import config_operation, file_operation

logger = getLogger(__name__)


def send_python_command(command: str, file_name: str) -> None:
    """Send to Maya python command.

    Args:
        command (str): Maya python command.
        file_name (str): The name of the command file.

    Raises:
        socket.error: Socket error occurred.Maybe Maya is not running or the port is not open.

    """
    # Get port number
    port_number = config_operation.get_port_number()

    # Make command file to maya path.
    _ = file_operation.create_command_file(command, file_name).replace('\\', '/')

    # Set send command
    package_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    send_command = (
        f"import {package_name}.maya.maya_main; {package_name}.maya.maya_main.execute_command('{file_name}')\n"
    )

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to Maya
        client.connect(("localhost", int(port_number)))
        client.send(send_command.encode())

        logger.debug(f"Send command: {send_command}")

    except socket.error as e:
        logger.exception("Socket error occurred.Maybe Maya is not running or the port is not open.")
        raise socket.error(e)
    finally:
        client.close()


def get_json_data(file_name: str) -> dict:
    """Get json data from file.

    Args:
        file_name (str): The name of the command file.

    Returns:
        dict: Json data.

    """
    # Get file path
    file_path = file_operation.get_result_file(file_name)

    # Get json data
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    logger.debug(f'Get json data: {json_data}')

    return json_data
