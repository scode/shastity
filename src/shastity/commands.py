# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
Operational command interface to shastity.

Provides an easy-to-use high-level library interface to invoking all
of shastities main functions, de-coupled from the normal command line
interface.

This is the public interface intended for other software to use for
invoking shastity as a library rather than a shell tool, for tighter
integration.

Commands
========

Commands are named operation that can be executed. A command takes
some number (possibly zero) of positional arguments, and potentially
some number of options on a key/value basis.

In concrete terms, each command will have associated with it::

  - Its name.
  - Information about positional arguments for purpose of display to humans.
  - Information about options that may apply to the command.

In plain python, a command C with positional arguments pos1, pos2,
... poN and a set of options O (in the form of a Configuration
instance) translates to a function call on this module of the form:

  C(pos1, pos2, ..., posN, options=O)

The concept is specifically meant to translate well into a command
line interface while still being fairly idiomatic and usable as a
library interface, while keeping the implementation identical.
"""

from __future__ import absolute_import
from __future__ import with_statement

import shastity.options as options
import shastity.traversal as traversal
import shastity.manifest as manifest
import shastity.filesystem as filesystem
import shastity.persistence as persistence
import shastity.materialization as materialization
import shastity.storagequeue as storagequeue
import shastity.backends.s3backend as s3backend
import shastity.backends.gpgcrypto as gpgcrypto

# In the future we'll have groups of commands too, or else command
# listings to the user become too verbose.

class Command(object):
    def __init__(self, name, args, options, description=None, long_help=None):
        """
        @param name: Name - string.
        @param args: List of arguments (list of name strings for human use).
        @param options: Configuration instance for the command.
        @param description: Short one-liner description, if given.
        @param long_help: Long potentially multi-line description, if given.
        """
        self.name = name
        self.args = args
        self.options = options
        self.description = description
        self.long_help = long_help

_all_commands = [ Command('persist',
                          ['src-path', 'dst-uri'],
                          options.GlobalOptions(),
                          description='Persist (backup) a directory tree.'),
                  Command('materialize',
                          ['src-uri', 'dst-path'],
                          options.GlobalOptions(),
                          description='Materialize (restore) a directory tree.'),
                  Command('verify',
                          ['src-path', 'dst-uri'],
                          options.GlobalOptions(),
                          description='Verify that a directory tree matches that which has previously been persisted.'),
                  Command('garbage-collect',
                          ['dst-uri'],
                          options.GlobalOptions(),
                          description='Garbage collect backend, removing unreferenced data (thus reclaiming space).'),
                  Command('test-backend',
                          ['dst-uri'],
                          options.GlobalOptions(),
                          description='Perform tests on the backend to confirm it works.'),
                  Command('list-manifest',
                          ['uri'],
                          options.GlobalOptions(),
                          description='List names of manifests'),
                  ]

def all_commands():
    """
    Returns a list of all commands. The order of the list is significant.
    """
    return _all_commands

def has_command(name):
    """
    Convenience function to check whether there is a command by the
    given name.
    """
    return (len([ cmd for cmd in all_commands() if cmd.name == name]) > 0)

def get_command(name):
    matching = [ cmd for cmd in _all_commands if cmd.name == name]

    assert len(matching) == 1

    return matching[0]

CONCURRENCY = 10
def make_backend(dst_uri):
    ret = s3backend.S3Backend(dst_uri)
    #if 'manifest' in dst_uri:
    ret = gpgcrypto.DataCryptoGPG(ret, 'hejsan')
    ret = gpgcrypto.NameCrypto(ret, 'hejsan')
    return ret

def persist(src_path, dst_uri, config):
    mpath, label, dpath = dst_uri.split(',')
    fs = filesystem.LocalFileSystem()
    traverser = traversal.traverse(fs, src_path)
    sq = storagequeue.StorageQueue(lambda: make_backend(dpath),
                                   CONCURRENCY)
    mf = list(persistence.persist(fs,
                                  traverser,
                                  None,
                                  src_path,
                                  sq,
                                  blocksize=2000))
    manifest.write_manifest(make_backend(mpath), label, mf)

def materialize(src_uri, dst_path, config):
    mpath, label, dpath = src_uri.split(',')
    fs = filesystem.LocalFileSystem()
    fs.mkdir(dst_path)
    mf = list(manifest.read_manifest(make_backend(mpath),
                                     label))
    sq = storagequeue.StorageQueue(lambda: make_backend(dpath),
                                   CONCURRENCY)
    materialization.materialize(fs, dst_path, mf, sq)


def list_manifest(uri):
    pass
    
def verify(src_path, dst_uri, config):
    raise NotImplementedError('very not implemented')

def garbage_collect(config, dst_uri):
    raise NotImplementedError('garbage_collect not implemented')

def test_backend(config, dst_uri):
    raise NotImplementedError('test-backend not implemented')
