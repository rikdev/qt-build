# coding: utf-8
"""Module to run jom (multithreaded analogue nmake)."""

import os
from .common import check_call_cmd
from .nmake import nmake

if os.name != 'nt':
    raise ImportError('{} is currently only supported on Windows system.'
                      ''.format(os.path.basename(__file__)))


_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

def jom(*nargs, **kwargs):
    """Run jom.exe if it exists otherwise run nmake"""
    jom_path = os.path.join(_ROOT_DIR, 'bin', 'jom.exe')
    if os.path.exists(jom_path):
        return check_call_cmd(jom_path, *nargs, **kwargs)
    else:
        return nmake(*nargs, **kwargs)


def make(*nargs, **kwargs):
    """Alias for jom"""
    return jom(*nargs, **kwargs)
