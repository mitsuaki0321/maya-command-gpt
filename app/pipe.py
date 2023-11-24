"""
Send command to Maya and get response.

Overview:
    This module is used for sending commands to Maya.

Functions:
    send_python_command: Send to Maya python command.
    get_json_data: Get json data from file.

"""

import datetime
import json
import os
import shutil
import socket
from logging import getLogger

from . import config_operation

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
    file_path = _create_command_file(command, file_name).replace('\\', '/')

    # Set send command
    package_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    send_command = (
        f"import {package_name}.maya.maya_main; {package_name}.maya.maya_main.execute_command('{file_path}')\n"
    )

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to Maya
        client.connect(("localhost", port_number))
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
    result_dir = config_operation.get_result_dir()
    file_path = os.path.join(result_dir, f'{file_name}.json')

    # Get json data
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    logger.debug(f'Get json data: {json_data}')

    return json_data


def _create_command_file(command: str, file_name: str, tail: str = 'py') -> str:
    """Create a command file for Maya.

    Args:
        command (str): Maya python command.
        file_name (str): The name of the command file.
        tail (str, optional): The tail of the command file. Defaults to 'py'.

    Returns:
        str: The path to the command file.

    """
    # Get file path
    python_dir = config_operation.get_python_dir()
    file_path = os.path.join(python_dir, f'{file_name}.{tail}')

    # Make backup file
    back_up_file = _make_backup_file(file_name)

    logger.debug(f'Make backup file: {back_up_file}')

    # Write command
    with open(file_path, 'w') as file:
        file.write(command)

    logger.debug(f'Made command file: {file_path}')

    return file_path


def _make_backup_file(file_name: str, tail: str = 'py') -> str:
    """Make a backup of the file.

    Args:
        file_name (str): The name of the file to backup.
        tail (str, optional): The tail of the file. Defaults to 'py'.

    Returns:
        str: The path to the backup file.
             Returns None if the file does not exist.

    """
    output_python_dir = config_operation.get_python_dir()

    file_path = os.path.join(output_python_dir, f'{file_name}.{tail}')
    if not os.path.exists(file_path):
        return

    # Create backup folder
    folder_path = os.path.join(output_python_dir, file_name)
    os.makedirs(folder_path, exist_ok=True)

    # Create backup file
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    backup_file_path = os.path.join(folder_path, f'{file_name}_{timestamp}.{tail}')

    move_file_path = shutil.move(file_path, folder_path)
    os.rename(move_file_path, backup_file_path)

    return backup_file_path
