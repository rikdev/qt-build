# coding: utf-8
"""Module to run nmake."""

import os
from .common import check_call_cmd

if os.name != 'nt':
    raise ImportError('{} is currently only supported on Windows system.'
                      ''.format(os.path.basename(__file__)))


def nmake(*nargs, **kwargs):
    """nmake.exe runner"""
    kwargs['shell'] = True
    return check_call_cmd('nmake', *nargs, **kwargs)

def make(*nargs, **kwargs):
    """Alias for nmake"""
    return nmake(*nargs, **kwargs)
