# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Takes stream(s) of (path, metadata) and persists to backends.
'''

from __future__ import absolute_import
from __future__ import with_statement

import  os.path

import shastity.filesystem as filesystem
import shastity.hash as hash
import shastity.logging as logging
import shastity.storagequeue as storagequeue

DEFAULT_BLOCKSIZE = 1024*1024
DEFAULT_HASHER = hash.make_hasher('sha512')

log = logging.get_logger(__name__)

def _next_block(f, blocksize):
    parts = []
    sofar = 0

    while sofar < blocksize:
        part = f.read(blocksize - sofar)
        if len(part) == 0:
            break # eof
        
        parts += part
        sofar += len(part)

    return ''.join(parts)

def _persist_file(fs,
                  path,
                  basepath,
                  meta,
                  sq,
                  blocksize=DEFAULT_BLOCKSIZE,
                  hasher=DEFAULT_HASHER):
    '''Persist a single file and return its entry to be yielded back
    to the parent caller. Parameters match those of persist().'''
    # TODO: fstat() after open to make sure we are not subject to
    # races. This particular case is important because regardless of
    # races in directory traversal, we definitely do not want to store
    # actual data under incorrect permissions.

    # TODO #2: Block devices and major/minor preservation. Bah.

    assert path.startswith(basepath)
    assert basepath.endswith('/') \
        or (basepath != '' and path.startswith(basepath + '/')) \
        or (basepath != '' and path == basepath)

    if meta.is_symlink:
        return (path, meta, [])
    elif meta.is_directory:
        return (path[len(basepath):], meta, [])
    else:
        hashes = []

        with fs.open(path, "r") as f:
            while True:
                block = _next_block(f, blocksize)
                if len(block) == 0:
                    break
                
                algo, hash = hasher(block)
                hashes.append((algo, hash))
                sq.enqueue(storagequeue.PutOperation(name=hash,
                                                     data=block))
            return (path[len(basepath):], meta, hashes)

def persist(fs,
            traversal,
            incremental,
            basepath,
            sq,
            blocksize=DEFAULT_BLOCKSIZE,
            hasher=DEFAULT_HASHER):
    '''Take an incoming traversal stream and persist in backing
    storage, while yielding appropriate (path, metadata, blocks)
    tuples. The third entry in that tuple is a list of (algo, hash)
    tuples.

    @param fs: File system from which to read file contents.
    @param traversal: Generator producting (path, metadata) entries.
    @param incremental: Incremental entry produced for a previous backup relative
                        to which we are to optimize away file reading/hashing/encryption.
    @param basepath: Base path (prefix) of backup.
    @param sq: Storage queue to which to write files contents.
    '''
    assert incremental is None, 'incremental optimization not yet implemented'
    
    for path, meta in traversal:
        # Future: Do traversal/incremental optimization logic here.
        yield _persist_file(fs, path, basepath, meta, sq)

    sq.wait()


