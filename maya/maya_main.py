"""
This module is a module for executing Maya commands.
After execution, it sends a webhook notification to the FastAPI server.

Classes:
    CommandResponse: Maya command response.

Functions:
    execute_command: Execute a Python file and save its return value to a JSON file.
    send_webhook_notification: Send a webhook notification to the FastAPI server.

"""

import importlib.util
import json
import os
import urllib.request
from typing import Any

from ..app import config_operation


class CommandResponse:
    """Maya command response."""

    def __init__(self):
        self.__status = 1
        self.__result = None
        self.__error_log = None

    def set_status(self, value: int = 1):
        self.__status = value

    def update_result(self, value: Any):
        self.__result = self.validate_json(value)

    def update_error_log(self, value: str):
        self.__error_log = self.validate_json(value)

    def validate_json(self, value: Any):
        """Validate the value.Check if it is JSON serializable.

        Args:
            result (Any): The result value.

        Raises:
            ValueError: The result value is not JSON serializable.

        Returns:
            Any: The result value.

        """
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            raise ValueError("Provided value is not JSON serializable")

    def to_dict(self):
        status = self.__status == 1 and "Success" or "Failed"
        return {"Status": status, "Result": self.__result, "ErrorLog": self.__error_log}


def execute_command(file_path: str) -> None:
    """Execute a Python file and save its return value to a JSON file.

    Note:
        This function is called by the Maya command.
        If the Maya command completes successfully, put the return value in Result and save it to a JSON file.
        If it fails, put the error log in ErrorLog and save it to a JSON file.

    Raises:
        AttributeError: main() is not defined in the command file.
        Exception: Other exceptions. This exception is often raised when a Maya command fails.

    """
    # Get script name
    file_name, _ = os.path.splitext(os.path.basename(file_path))

    # Make json path
    result_dir = config_operation.get_result_dir()
    json_file = os.path.join(result_dir, f'{file_name}.json')

    # Execute and save output
    command_response = CommandResponse()

    try:
        spec = importlib.util.spec_from_file_location(file_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            raise AttributeError("main() is not defined in the command file.")

        result = module.main()

        if result:
            command_response.update_result(result)

        with open(json_file, "w") as file:
            json.dump(command_response.to_dict(), file, indent=4)

    except Exception as e:
        command_response.update_error_log(str(e))
        command_response.set_status(0)
        with open(json_file, "w") as file:
            json.dump(command_response.to_dict(), file, indent=4)

    # Send notification
    __send_webhook_notification()


def __send_webhook_notification() -> None:
    """Send a webhook notification to the FastAPI server.

    Args:
        webhook_url (str): The URL of the webhook.
    """
    url = f'{config_operation.get_url()}/maya/webhook'
    data = json.dumps({"message": "Maya Command Completed"}).encode()

    req = urllib.request.Request(url, data=data, headers={'content-type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read()
            print("Notification sent, response:", response_body)
    except urllib.error.URLError as e:
        print(f"Error sending notification: {e}")