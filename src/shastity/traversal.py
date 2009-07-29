# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Traversal of a file system tree, producing a list of paths and their
metadata.
'''

from __future__ import absolute_import
from __future__ import with_statement

import os.path

import shastity.filesystem as filesystem
import shastity.logging as logging
import shastity.metadata as metadata

log = logging.get_logger(__name__)

class NotADirectory(Exception):
    pass

def _traverse_dir(fs, path):
    files = fs.listdir(path)
    
    # sort files so that we emit them in a deterministic order; this
    # is necessary to allow for streaming comparisons between two
    # streams of traversal entries (useful for ctime based
    # optimization of incremental backups)
    files.sort()
    
    # this is a bit tricky to do correctly, and we don't really. we
    # should check to see what other tools do. in general, traversing
    # a live file system has all sorts of race conditions. one way to
    # avoid problems is to always open() and fstat() instead of
    # stat():ing the path, but that will cause useless overhead as
    # well as making atime more useless.
    #
    # so we go for a path based approach. a caller can then choose to
    # fstat() an open fd to get the correct permissions, to at least
    # avoid intra-user security issues.
    #
    # of course we should really recommend to users that they never
    # backup live file systems if they can avoid it.
    for f in files:
        fpath = os.path.join(path, f)
        fmeta = fs.lstat(fpath)

        yield (fpath, fmeta)

        if fmeta.is_directory and not fmeta.is_symlink:
            for recpath, recmeta in _traverse_dir(fs, fpath):
                yield recpath, recmeta

def traverse(fs, path):
    '''
    Traverse the file system, rooting the traversal at the given path,
    and yield, for each file system entry, a tuple (path,
    metadata). The latter element is a FileMetaData instance.

    We require that the path is a directory (because it seems to make
    sense to warn if it is not; we could support otherwise).

    @type fs FileSystem
    @param fs Filesystem backend to traverse.
    @param path Path to root of traversal.
    '''
    # TODO: what to do about the base path changing? should we resolve
    # the symlink once and keep the real path for consistency? that
    # would only help in the particular case of symlinks of course,
    # and not e.g. umounts etc. What do other tools do, what does tar
    # do for example?

    if fs.is_symlink(path) or not fs.is_dir(path):
        raise NotADirectory(path)

    yield (path, fs.lstat(path))
    
    for path, metadata in _traverse_dir(fs, path):
        yield (path, metadata)
