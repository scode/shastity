# -*- coding: utf-8 -*-

# Copyright (c) 2008 Peter Schuller <peter.schuller@infidyne.com>

"""
Thin wrapper around the standard logging module. The remainder of
shastity should never refer directly to the standard logging module.
"""

from __future__ import absolute_import
from __future__ import with_statement

import logging

# Mirror log levels, and add the missing (why!??!?!) NOTICE.
DEBUG = logging.DEBUG
INFO = logging.INFO
NOTICE = (logging.WARNING + logging.INFO) / 2
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# make sure there was room between INFO and WARNING
assert NOTICE > logging.INFO
assert NOTICE < logging.WARNING

# and make sure we have not misunderstood the numerical interpretation
# of levels
assert INFO < WARNING

def get_logger(name):
    """
    Our version of logging.getLogger().
    """
    return logging.getLogger(name)

