# -*- coding: utf-8 -*-
"""Module with cross platform helpers"""

import subprocess


def check_call_cmd(cmd, cmd_args=None, *nargs, **kwargs):
    """Different command and arguments for subprocess.check_call"""
    command = [cmd]
    if cmd_args is not None:
        command += cmd_args if isinstance(cmd_args, list) else [cmd_args]
    return subprocess.check_call(command, *nargs, **kwargs)
