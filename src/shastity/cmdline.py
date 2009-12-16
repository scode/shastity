# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
Command line interface to shastity.

Provdes an implementation of command line argument parsing and
translating the results into appropriate calls to the
shastity.operations module.
"""

from __future__ import absolute_import
from __future__ import with_statement

import logging
import optparse
import sys

class CommandLineError(Exception):
    """
    Raised to indicate a problem with the command line.
    """
    pass

def _build_parser():
    parser = optparse.OptionParser()

    return parser

def _interpret_cmdline(options, args):
    raise CommandLineError('not implemented')

def main():
    try:
        option_parser = _build_parser()

        options, args = option_parser.parse_args()

        operation, args, kwargs, config = _interpret_cmdline(options, args)

        getattr(operations, operation)(*(args + (config,)))

        sys.exit(0)
    except CommandLineError, e:
        logging.error('shastity: command line error: %s', unicode(e))
    except Exception, e:
        logging.exception('shastity: error: %s', unicode(e))

    sys.exit(1) # todo: communiate more detail to callers

