# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import os
import shutil
import tempfile
import unittest

import shastity.backend as backend
import shastity.backends.directorybackend as directorybackend
import shastity.backends.memorybackend as memorybackend
import shastity.backends.s3backend as s3backend
import shastity.logging as logging
import shastity.storagequeue as storagequeue

log = logging.get_logger(__name__)

# this code shares a lot with the backend tests, however we do want to
# keep them separate, but we also do have a specific reason to support
# the use of multiple backends in these tests, since the actual
# real-life behavior of backends in the presence of concurrency is
# best tested indirectly via the storage queue tests.

PREFIX = 'shastity_unittest_'

CONCURRENCY = 10

def prefix(name):
    '''Trivial convenience function for constructing a PREFIX:ed filename.'''
    return PREFIX + name

class StorageQueueBaseCase(object):

    def setUp(self):
        with self.make_backend() as backend:
            if not backend.exists():
                backend.create()

            # We do not assume the backend is empty at the time the test
            # starts, but we do assume that we can put, get and delete any
            # file beginning with PREFIX. In order to ensure we can re-run
            # tests in an idempotent fashion, we clean up pre-existing
            # files of tests first.
            fnames = self.get_testfiles(backend)

            for fname in fnames:
                backend.delete(fname)

    def tearDown(self):
        pass

    def get_testfiles(self, backend):
        return [ name for name in backend.list() if name.startswith(PREFIX)]

    def test_basic(self):
        with storagequeue.StorageQueue(lambda: self.make_backend(), CONCURRENCY) as sq:
            sq.enqueue(storagequeue.PutOperation(prefix('test1'), 'data1'))
            sq.enqueue(storagequeue.PutOperation(prefix('test2'), 'data2'))
            sq.enqueue(storagequeue.PutOperation(prefix('test3'), 'data3'))
            sq.wait()
            sq.enqueue(storagequeue.GetOperation(prefix('test1')))
            sq.enqueue(storagequeue.GetOperation(prefix('test2')))
            sq.enqueue(storagequeue.GetOperation(prefix('test3')))
            sq.barrier()
            sq.enqueue(storagequeue.DeleteOperation(prefix('test1')))
            sq.enqueue(storagequeue.DeleteOperation(prefix('test2')))
            sq.enqueue(storagequeue.DeleteOperation(prefix('test3')))
            sq.wait()
            

class MemoryBackendTests(StorageQueueBaseCase, unittest.TestCase):
    def make_backend(self):
        return memorybackend.MemoryBackend('memory', dict(max_fake_delay=0.1))

class DirectoryBackendTests(StorageQueueBaseCase, unittest.TestCase):
    def make_backend(self):
        return directorybackend.DirectoryBackend(self.tempdir)

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(suffix='-shastity_directory_backend_unittest')
        log.debug('using temporary directory %s', self.tempdir)

        StorageQueueBaseCase.setUp(self)

    def tearDown(self):
        StorageQueueBaseCase.tearDown(self)

        log.debug('cleaning temporary directory %s', self.tempdir)
        shutil.rmtree(self.tempdir)

if os.getenv('SHASTITY_UNITTEST_S3_BUCKET') != None:
    class S3BackendTests(StorageQueueBaseCase, unittest.TestCase):
        def make_backend(self):
            return s3backend.S3Backend(os.getenv('SHASTITY_UNITTEST_S3_BUCKET')) # todo

if __name__ == "__main__":
    unittest.main()
