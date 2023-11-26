"""
This module is a module for executing Maya commands.
After execution, it sends a webhook notification to the FastAPI server.

Note:
    This module consists of modules that can be imported in Maya.

    If the processing in Maya takes more than the number of seconds
    specified by the TIMEOUT variable after execution, it returns a timeout error.

Classes:
    CommandResponse: Maya command response.

Functions:
    execute_command: Execute a Python file and save its return value to a JSON file.
    send_webhook_notification: Send a webhook notification to the FastAPI server.

"""
import concurrent.futures
import importlib.util
import json
from typing import Any

from ..app import file_operation

# Timeout settings
TIME_OUT = 15


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


def execute_command(file_name: str) -> None:
    """Execute a Python file and save its return value to a JSON file.

    Args:
        file_name (str): The name of the command file.

    Note:
        This function is called by the Maya command.
        If the Maya command completes successfully, put the return value in Result and save it to a JSON file.
        If it fails, put the error log in ErrorLog and save it to a JSON file.

    Raises:
        AttributeError: main() is not defined in the command file.
        Exception: Other exceptions. This exception is often raised when a Maya command fails.

    """
    print('Execute command')
    # Make json path
    json_file = file_operation.get_result_file(file_name)

    # Execute and save output
    command_response = CommandResponse()

    print('Execute command start')
    try:
        python_file_path = file_operation.get_python_file(file_name)
        spec = importlib.util.spec_from_file_location(file_name, python_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "main"):
            raise AttributeError("main() is not defined in the command file.")

        result = module.main()
        if result:
            # Get result
            command_response.update_result(result)

    #     # Timeout settings
    #     with concurrent.futures.ThreadPoolExecutor() as executor:
    #         future = executor.submit(module.main)
    #         result = future.result(timeout=TIME_OUT)

    #         if result:
    #             # Get result
    #             command_response.update_result(result)

    # except concurrent.futures.TimeoutError:
    #     command_response.update_error_log(
    #         f"TimeoutError: The command took more than {TIME_OUT} seconds to execute, resulting in a timeout error."
    #     )
    #     command_response.set_status(0)
    except Exception as e:
        # If error from Maya command, get error log
        command_response.update_error_log(str(e))
        command_response.set_status(0)
    finally:
        # Save json file
        with open(json_file, "w") as file:
            json.dump(command_response.to_dict(), file, indent=4)
