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

  C(options=O, pos1, pos2, ..., posN)

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
                  Command('common-blocks',
                          ['uri'],
                          options.GlobalOptions(),
                          description='Find common blocks in two or more manifests'),
                  Command('get-block',
                          ['uri', 'block-name', 'local-name'],
                          options.GlobalOptions(),
                          description='Get a backend block by its plaintext name'),
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

CONCURRENCY = 10 # TODO: hard-coded
def flatten(z):
    return reduce(lambda x,y: x + y, z)

def get_all_manifests(be):
    return [(x, list(manifest.read_manifest(be, x)))
            for x in manifest.list_manifests(be)]

def get_all_blockhashes(mfs, unique = True):
    ret = flatten([x[2] for x in flatten(mfs)])
    if unique:
        ret = list(set(ret))
    return ret

def persist(config, src_path, dst_uri):
    mpath, label, dpath = dst_uri.split(',')

    be = get_backend_factory(mpath)()
    mfs = get_all_manifests(be)
    if len(mfs) != 0:
        mfs = zip(*mfs)[1]
        uploaded = get_all_blockhashes(mfs)
    else:
        uploaded = []

    # run persist
    fs = filesystem.LocalFileSystem()
    traverser = traversal.traverse(fs, src_path)
    sq = storagequeue.StorageQueue(get_backend_factory(dpath),
                                   CONCURRENCY)
    mf = list(persistence.persist(fs,
                                  traverser,
                                  None,
                                  src_path,
                                  sq,
                                  blocksize=2000,
                                  skip_blocks=uploaded))
    manifest.write_manifest(be, label, mf)

def materialize(config, src_uri, dst_path):
    mpath, label, dpath = src_uri.split(',')
    fs = filesystem.LocalFileSystem()
    fs.mkdir(dst_path)
    mf = list(manifest.read_manifest(get_backend_factory(mpath)(),
                                     label))
    sq = storagequeue.StorageQueue(get_backend_factory(dpath),
                                   CONCURRENCY)
    materialization.materialize(fs, dst_path, mf, sq)



def get_backend_factory(uri):
    """get_backend_factory(uri)

    Parses a URI and creates the factory.

    TODO: crypto stuff are added by magic, and only s3 is supported
    """
    type,ident = uri.split(':',1)
    if type == 's3':
        ret = lambda: s3backend.S3Backend(ident)
        ret2 = lambda: gpgcrypto.DataCryptoGPG(ret(), 'hejsan')
        ret3 = lambda: gpgcrypto.NameCrypto(ret2(), 'hejsan')
        return ret3
    raise NotImplementedError('backend type %s not implemented' % (type))

def list_manifest(config, uri):
    b = get_backend_factory(uri)()
    lmfs = list(get_all_manifests(b))
    lmfs.sort()

    if not len(lmfs):
        print "Found no manifests"
        return

    labels,mfs = zip(*lmfs)
    uploaded = get_all_blockhashes(mfs, unique=False)

    print "%-20s %6s %7s %7s" % ('Manifest', 'Files', 'Blocks', 'Shared')

    for label,mf in lmfs:
        shared = 0
        blocks = flatten([x[2] for x in mf])
        for h in blocks:
            if uploaded.count(h) > 1:
                shared += 1
        print "%-20s %6d %7d %7d" % (label,
                                    len(mf),
                                    len(blocks),
                                    shared)

def common_blocks(config, uri, *mf_names):
    b = get_backend_factory(uri)()
    mfs = [manifest.read_manifest(b, x) for x in mf_names]
    blocks = [get_all_blockhashes([x]) for x in mfs]
    all_blocks = flatten(blocks)
    before = [len(x) for x in blocks]
    [ [bl.remove(x) for bl in blocks]
       for x in list(set(all_blocks))
       if all_blocks.count(x) == len(mf_names)
       ]
    after = [len(x) for x in blocks]
    for nm,bf,af in zip(mf_names,before,after):
        print '%d unique in %s' % (af, nm)
    print '%d in common' % (before[0] - after[0])


def get_block(config, uri, block_name, local_name=None):
    if local_name is None:
        local_name = block_name
    b = get_backend_factory(uri)()
    open(local_name, 'w').write(b.get(block_name))

def verify(config, src_path, dst_uri):
    raise NotImplementedError('very not implemented')

def garbage_collect(config, dst_uri):
    raise NotImplementedError('garbage_collect not implemented')

def test_backend(config, dst_uri):
    raise NotImplementedError('test-backend not implemented')
