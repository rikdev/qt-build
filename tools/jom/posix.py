# -*- coding: utf-8 -*-
"""Module to run utilities for Posix"""

import os
from .common import check_call_cmd

if os.name != 'posix':
    raise ImportError('{} is currently only supported on posix-like system.'
                      ''.format(os.path.basename(__file__)))


def make(*nargs, **kwargs):
    """make runner"""
    return check_call_cmd('make', *nargs, **kwargs)
