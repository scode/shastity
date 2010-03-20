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
import shastity.options as options
import shastity.verbosity as verbosity

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

def _make_config(cmdname):
    """
    @param cmdname: Command name of None (for global options).
    @return Configuration instance.
    """
    if cmdname is not None:
        cmd = commands.get_command(cmdname)
        opts = cmd.options
    else:
        opts = options.GlobalOptions()

    return opts

def _build_parser():
    cmdname = _find_command()

    if cmdname is not None and not commands.has_command(cmdname):
        raise CommandLineError('unknown command: %s (see --help)' % (cmdname,))

    config = _make_config(cmdname)

    cmd = commands.get_command(cmdname) if cmdname is not None else None

    # Epilog newlines/formatting is squashed by option parser. Something else
    # to fix.
    if cmdname is None:
        epilog = ([ "Available commands: " ] +
                  [ cmd.name for cmd in sorted(commands.all_commands()) ])
        usage = '%prog <command> [args] [options]'
    else:
        epilog = ['%s: %s' % (cmdname, cmd.__doc__)]
        usage = '%%prog %s [args] [options]' % (cmdname,)

    parser = optparse.OptionParser(usage=usage,
                                   epilog=' '.join(epilog))

    for opt in config.options():
        opt.populate_optparser(parser)

    return parser

def _interpret_cmdline(options, args):
    cmdname = _find_command()

    config = _make_config(cmdname) # should use guaranteed-same as parser builder

    for opt in config.options():
        opt.interpret_optparser_options(options)

    return (cmdname, sys.argv[2:], dict(), config)

def main():
    try:
        option_parser = _build_parser()

        options, args = option_parser.parse_args()

        command, args, kwargs, config = _interpret_cmdline(options, args)

        logging.basicConfig(level=verbosity.to_level(config.get_option('verbosity').get_required()))

        if command is None:
            option_parser.print_help(file=sys.stderr)
            sys.exit(1)

        getattr(commands, command.replace('-','_'))(config, *args)
        sys.exit(0)

    except CommandLineError, e:
        logging.error('shastity: command line error: %s', unicode(e))
    except Exception, e:
        logging.exception('shastity: error: %s', unicode(e))

    # On demand, we should have some errors yield well-defined return
    # codes. For now, we always return 1 on failure.
    sys.exit(1)

