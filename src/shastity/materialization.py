# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Materializes a stream of (path, metadata) entries into an actual file
system.
'''

from __future__ import absolute_import
from __future__ import with_statement

import  os.path

import shastity.filesystem as filesystem
import shastity.logging as logging

log = logging.get_logger(__name__)

def materialize(fs, path, entryiter, storagequeue):
    '''
    @type fs FileSystem instance.
    @param fs File system into which to materialize the stream.

    @param path The path in the file system at which to materialize the stream to.

    @type entryiter iterable yielding (path, metadata) tuples
    @param entryiter The generator of entries to materialize.

    @type storagequeue StorageQueue
    @param storagequeue Storage queue via which to perform read operations necessary in
                        order to populate the tree.
    '''
    pass
