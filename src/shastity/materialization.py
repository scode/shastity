# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Materializes a stream of (path, metadata) entries into an actual file
system.
'''

from __future__ import absolute_import
from __future__ import with_statement

import os.path
import threading

import shastity.filesystem as filesystem
import shastity.logging as logging
import shastity.storagequeue as storagequeue

log = logging.get_logger(__name__)

class DestinationPathNotDirectory(Exception):
    pass

def materialize(fs, destpath, entryiter, sq):
    '''
    @type fs FileSystem instance.
    @param fs File system into which to materialize the stream.

    @param destpath The path in the file system at which to materialize the stream to.

    @type entryiter iterable yielding (path, metadata, hashes) tuples
    @param entryiter The generator of entries to materialize.

    @type sq StorageQueue
    @param sq Storage queue via which to perform read operations necessary in
              order to populate the tree.
    '''
    # We traverse the list in order, thus ensuring that directories
    # are created prior to their contents. However, we also want to
    # make sure that concurrency in the storage backend can be
    # utilized, so we submit multiple requests concurrently to
    # whatever extent possible, relying on the storage queue to block
    # us when the concurrency limit has been reached.
    #
    # We rely on callback semantics of the storage queue in order to
    # achieve this result. We seemingly submit requests in an
    # unlimited fashion, but because the callbacks we register with
    # get operations block until they are done and all data in memory
    # can be thrown away, we ensure that we limit our actual
    # concurrency to that of the storage queue without having to
    # implement rate limiting or concurrency limitation here.
    #
    # We could allow callbacks to write arbitrary blocks to file as
    # they come in, but it would mean that the I/O characteristics of
    # the writes against the operating system is non-sequential, and
    # it violates POLA for the user who, when seeing a file of N
    # bytes, will probably conclude that N bytes have been
    # restored. If parts of the file are sparse because of
    # out-of-order writes, this could cause quite a lot of
    # confusion. So even though it is strictly speaking sub-optimal
    # from a performance standpoint, we will require sequential
    # writes. This means that the callback for block n for a file,
    # will not return until the callback for block n - 1 has returned.
    #
    # We accomplish this by creating a FileMaterialization instance
    # for each file that we are restoring, which is the
    # synchronization point for the callbacks.

    class FileMaterialization:
        """
        TODO: Handle I/O errors (propagate to callers of write_block).
        """
        def __init__(self, fname, totblocks, fobj):
            """
            @param fname: File name being materialized.
            @param totblocks: Total number of expected blocks.
            @param fobj: File object to which to write blocks.
            """
            self.__fname = fname
            self.__totblocks = totblocks
            self.__fobj = fobj

            self.__cond = threading.Condition()
            self.__last_block = -1 # last block written, -1 if no block written

        def write_block(self, bytestr, block_num):
            """
            Blocks until block (block_num - 1) has been written, and
            writes the block.

            @param bytestr: Byte string to write to file.
            @param block_num: The block number (first block is 0).
            """
            with self.__cond:
                while self.__last_block != block_num - 1:
                    self.__cond.wait()

            assert self.__last_block == block_num - 1

            log.info('materializing block %d of file %s', block_num, self.__fname)
            self.__fobj.write(bytestr)

            with self.__cond:
                self.__last_block += 1
                assert self.__last_block == block_num

                if block_num == self.__totblocks - 1:
                    log.debug('fsync():ing after final block of %s', self.__fname)
                    self.__fobj.flush()
                    # todo: always, or optionally based on settings, delay fsync
                    # in order to avoid overhead.
                    fs.fsync(self.__fobj.fileno())
                    self.__fobj.close()

    if not fs.is_dir(destpath):
        raise DestinationPathNotDirectory(destpath)

    curdir = None
    for path, metadata, hashes in entryiter:
        local_path = os.path.join(destpath, path)

        log.info('materializing [%s]', path)

        assert not path.startswith('/')

        if metadata.is_directory:
            fs.mkdir(local_path)
            # TODO: fix perms
            curdir = path
        else:
            assert curdir is not None, 'no curdir - first entry not directory?'
            assert path.startswith(curdir), ('%s does not start with %s - out of order?'
                                             '' % (path, curdir))
            f = fs.open(local_path, 'w')
            # TODO: fix perms before any writing happens
            # TODO: and remember to optionally fsync to avoid security vuln in case
            #       of crash and out-of-order writes.
            m13n = FileMaterialization(fname=local_path,
                                       totblocks=len(hashes),
                                       fobj=f)
            blocknames = [ algohash[1] for algohash in hashes ]
            ops = [ storagequeue.GetOperation(name=blockname,
                                              callback=lambda bstr: m13n.write_block(bstr, block_num))
                    for block_num, blockname in enumerate(blocknames) ]
            for op in ops:
                sq.enqueue(op)



