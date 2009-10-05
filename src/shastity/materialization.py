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

class DestinationPathNotDirectory(Exception):
    pass

def materialize(fs, destpath, entryiter, storagequeue):
    '''
    @type fs FileSystem instance.
    @param fs File system into which to materialize the stream.

    @param destpath The path in the file system at which to materialize the stream to.

    @type entryiter iterable yielding (path, metadata, hashes) tuples
    @param entryiter The generator of entries to materialize.

    @type storagequeue StorageQueue
    @param storagequeue Storage queue via which to perform read operations necessary in
                        order to populate the tree.
    '''
    # We traverse the list in order, thus ensuring that directories
    # are created prior to their contents. However, we also want to
    # make sure that concurrency in the storage backend can be
    # utilized, so we submit multiple requests concurrently to
    # whatever extent possible, relying on the storage queue to block
    # us when the concurrency limit has been reached.

    if not fs.is_dir(destpath):
        raise DestinationPathNotDirectory(destpath)

    curdir = None
    for path, metadata, hashes in entryiter:
        log.info('materializing [%s]', path)

        assert not path.startswith('/')

        if metadata.is_directory:
            fs.mkdir(os.path.join(destpath, path))
            # TODO: fix perms
            curdir = path
        else:
            assert curdir is not None, 'no curdir - first entry not directory?'
            assert path.startswith(curdir), ('%s does not start with %s - out of order?'
                                             '' % (path, curdir))


