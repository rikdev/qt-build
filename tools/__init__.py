# coding: utf-8

import os
import sys

_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(_ROOT_DIR)
import jom

sys.path.append(os.path.join(_ROOT_DIR, 'PythonVCTools'))
import vctools
