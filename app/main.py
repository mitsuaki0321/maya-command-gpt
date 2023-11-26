"""
FastAPI server for Maya.

Usage:
    Maya settings:

    Open port in Maya:
        import mayacommandgpt.maya_settings
        mayacommandgpt.maya_settings.open_port()

    Start server:
    Run this server in terminal:
        uvicorn main:app --reload --port {port number}

    If you want to test it locally, access /docs and try send_command.
    If you want to send commands from GPTs, you need to expose the URL instead of using localhost.
    For this test, I used ngrok to expose the URL and perform the test.

    finally:
    Close port in Maya:
        import mayacommandgpt.maya_settings
        mayacommandgpt.maya_settings.close_port()

Functions:
    Command: Command model.
    maya_webhook: Receives a webhook from Maya.
    send_command: Receives a command, executes it in Maya, and sends back the return value.

"""
import asyncio
import os
import socket
from logging import getLogger

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import file_operation, pipe

logger = getLogger(__name__)

app = FastAPI()


class Command(BaseModel):
    """Command model.

    Note:
        command: Maya python command.

    """

    command: str
    file_name: str


@app.post("/maya/sendCommand")
async def send_python_command(command: Command) -> dict:
    """Main process. Sends a command to Maya and returns the result.

    Args:
        command (Command): Command model.

    Raises:
        HTTPException: If an error occurs, an exception occurs.
              the error message will be "OSError occurred: [error details]".

            - If a socket.error occurs (e.g., when Maya is not running or the port is not open),
              the error message will be "Socket error occurred: [error details]".

            - If any other Exception occurs, the error message will be "Error occurred: [error details]".

    Returns:
        dict: Return value from Maya.

    """
    try:
        # Delete result file
        file_operation.delete_result_file(command.file_name)

        # Send command to Maya
        pipe.send_python_command(command.command, command.file_name)

        # Wait for Maya to finish processing
        result_file = file_operation.get_result_file(command.file_name)
        while not os.path.exists(result_file):
            await asyncio.sleep(1.0)

        # Get return value from Maya
        data = pipe.get_json_data(command.file_name)

    except OSError as e:
        raise HTTPException(status_code=500, detail=f"OSError occurred: {e}")
    except socket.error as e:
        raise HTTPException(status_code=500, detail=f"Socket error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {e}")

    return data
