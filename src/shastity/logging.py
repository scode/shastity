# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

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

class FakeLogger(object):
    '''Fake logger mostly intended for unit testing. For its context
    managed life time it will patch away a given attribute with
    itself, mocking away the logging functions.'''
    def __init__(self, module, attrname):
        self.mocked_module = module
        self.mocked_attr = attrname
        self.real_log = getattr(module, attrname)

    def __enter__(self):
        setattr(self.mocked_module, self.mocked_attr, self)

    def __exit__(self, *args, **kwargs):
        setattr(self.mocked_module, self.mocked_attr, self.real_log)

    def log(self, *args, **kwargs):
        pass

    def critical(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def notice(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

# TODO: this is bad (to do this on module import).
logging.basicConfig()


