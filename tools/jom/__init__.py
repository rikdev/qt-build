# coding: utf-8

import os

if os.name == 'posix':
    from .posix import make
elif os.name == 'nt':
    from .jom import make
else:
    raise ImportError('Unsupported system {}'.format(os.name))
