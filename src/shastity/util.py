# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Misc utilities.
'''

import string
import sys
import traceback

def current_traceback(maxdepth = 25):
    '''
    @return A traceback similar to what the Python interpreter prints
            on leaked exceptions, describing the currently active
            exception.
    '''
    # why is there not a standard Python function to do this with a
    # minimum of fuss?

    type, value, tb = sys.exc_info()

    lines = traceback.format_tb(tb, maxdepth)
    lines.extend(traceback.format_exception_only(type, value))

    str = "Traceback (innermost last):\n"
    str = str + "%-20s %s" % (string.join(lines[:-1], ''),
                              lines[-1])

    return str
