import datetime
import os
import shutil
from logging import getLogger

from . import config_operation

logger = getLogger(__name__)


def get_result_file(file_name: str) -> str:
    """Get the result file path.

    Returns:
        str: The result file path.

    """
    # Get file path
    result_dir = config_operation.get_result_dir()
    file_path = os.path.join(result_dir, f'{file_name}.json')

    return file_path


def delete_result_file(file_name: str) -> None:
    """Delete the result file.

    Args:
        file_name (str): The name of the result file.

    """
    # Get file path
    result_dir = config_operation.get_result_dir()
    file_path = os.path.join(result_dir, f'{file_name}.json')

    # Delete file
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.debug(f'Delete result file: {file_path}')

    logger.debug(f'Not found result file then not delete result file: {file_path}')


def get_python_file(file_name: str) -> str:
    """Get the python file path.

    Returns:
        str: The python file path.

    """
    # Get file path
    python_dir = config_operation.get_python_dir()
    file_path = os.path.join(python_dir, f'{file_name}.py')

    return file_path


def make_backup_file(file_name: str, tail: str = 'py') -> str:
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
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    backup_file_path = os.path.join(folder_path, f'{file_name}_{timestamp}.{tail}')

    move_file_path = shutil.move(file_path, folder_path)
    os.rename(move_file_path, backup_file_path)

    return backup_file_path


def create_command_file(command: str, file_name: str, tail: str = 'py') -> str:
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
    back_up_file = make_backup_file(file_name)

    logger.debug(f'Make backup file: {back_up_file}')

    # Write command
    with open(file_path, 'w') as file:
        file.write(command)

    logger.debug(f'Made command file: {file_path}')

    return file_path
