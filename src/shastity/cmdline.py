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

import shastity.commands as commands

class CommandLineError(Exception):
    """
    Raised to indicate a problem with the command line.
    """
    pass

def _find_command():
    # We want to support the sub-command concept, but OptionParser has
    # no support for this. As a hack, we simply require that the first
    # argument be the command (if any). This should be fixed;
    # hopefully in the form an option parser library other than
    # optparse.

    if len(sys.argv) <= 1:
        return None
    elif sys.argv[1].startswith('-'):
        return None
    else:
        return sys.argv[1]

def _build_parser():
    parser = optparse.OptionParser()

    return parser

def _interpret_cmdline(options, args):
    cmdname = _find_command()

    return (cmdname, (), dict(), None)

def main():
    try:
        option_parser = _build_parser()

        options, args = option_parser.parse_args()

        command, args, kwargs, config = _interpret_cmdline(options, args)

        if command is None:
            option_parser.print_help(file=sys.stderr)
        else:
            if commands.has_command(command):
                getattr(commands, command)(*args, **(dict(config=config)))
            else:
                raise CommandLineError('unknown command: %s (see --help)' % (command,))

        sys.exit(0)
    except CommandLineError, e:
        logging.error('shastity: command line error: %s', unicode(e))
    except Exception, e:
        logging.exception('shastity: error: %s', unicode(e))

    sys.exit(1) # todo: communiate more detail to callers

