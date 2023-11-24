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

    finnaly:
    Close port in Maya: ( finally )
        import mayacommandgpt.maya_settings
        mayacommandgpt.maya_settings.close_port()

Functions:
    Command: Command model.
    maya_webhook: Receives a webhook from Maya.
    send_command: Receives a command, executes it in Maya, and sends back the return value.

"""

import asyncio
import socket
from logging import getLogger

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from . import pipe

logger = getLogger(__name__)

app = FastAPI()
notification_event = asyncio.Event()


class Command(BaseModel):
    """Command model.

    Note:
        command: Maya python command.
        file_name: The name of the command file without tail.

    """

    command: str
    file_name: str


@app.post("/maya/webhook")
async def maya_webhook(request: Request):
    """Receives a webhook from Maya.

    Args:
        request (Request): Request model.

    Returns:
        dict: Webhook data.

    """
    webhook_data = await request.json()
    print("Received webhook from Maya:", webhook_data)
    notification_event.set()

    return {"status": "received", "data": webhook_data}


@app.post("/maya/sendCommand")
async def send_command(command: Command) -> dict:
    """Receives a command, executes it in Maya, and sends back the return value.

    Args:
        command (Command): Command model.

    Raises:
        HTTPException: Socket error occurred.
                       Maybe Maya is not running or the port is not open.

    Returns:
        dict: Return value from Maya.


    """
    try:
        # Send command to Maya
        pipe.send_python_command(command.command, command.file_name)

        logger.debug(f"Apply command: {command.command}")

        # Wait for notification from Maya
        await notification_event.wait()

        # Get return value from Maya
        data = pipe.get_json_data(command.file_name)

        logger.debug(f"Return value: {data}")

        # Reset notification event
        notification_event.clear()
    except socket.error as e:
        raise HTTPException(status_code=500, detail=f"Socket error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {e}")

    return data
