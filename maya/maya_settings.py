"""
Maya settings.

Overview:
    This module is used in maya.

Functions:
    open_port: Open port.
    close_port: Close port.

"""

import maya.cmds as cmds

from ..app import config_operation


def open_port():
    """Open port.

    Args:
        port (int, optional): Port number. Defaults to 7001.

    """
    port_number = config_operation.get_port_number()
    cmds.commandPort(name=f':{port_number}', sourceType='python')


def close_port():
    """Close port.

    Args:
        port (int, optional): Port number. Defaults to 7001.

    """
    port_number = config_operation.get_port_number()
    cmds.commandPort(name=f':{port_number}', close=True)
