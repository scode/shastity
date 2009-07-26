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
            puts = [ storagequeue.PutOperation(prefix('test%s' % (n,)), str(n)) for n in xrange(0, 5) ]
            gets = [ storagequeue.GetOperation(prefix('test%s' % (n,))) for n in xrange(0, 5) ]
            dels = [ storagequeue.DeleteOperation(prefix('test%s' % (n,))) for n in xrange(0, 5) ]
            
            # PUT
            for p in puts:
                self.assertFalse(p.is_done())
                self.assertRaises(AssertionError, lambda: p.value())
                self.assertRaises(AssertionError, lambda: p.succeeded())
                sq.enqueue(p)

            sq.wait()

            for p in puts:
                self.assertTrue(p.is_done())
                self.assertTrue(p.succeeded())

            # GET + DELETE
            for g in gets:
                self.assertFalse(g.is_done())
                self.assertRaises(AssertionError, lambda: g.value())
                self.assertRaises(AssertionError, lambda: g.succeeded())
                sq.enqueue(g)
                
            sq.barrier()

            for d in dels:
                self.assertFalse(d.is_done())
                self.assertRaises(AssertionError, lambda: d.value())
                self.assertRaises(AssertionError, lambda: d.succeeded())
                sq.enqueue(d)

            sq.wait()

            for g in gets:
                self.assertTrue(p.is_done())
                self.assertTrue(p.succeeded())
                
            self.assertEqual([g.value() for g in gets], [ '0', '1', '2', '3', '4' ])

            for d in dels:
                self.assertTrue(d.is_done())
                self.assertTrue(d.succeeded())
                self.assertEqual(d.value(), None)
                
    def test_bad_get_fail(self):
        with logging.FakeLogger(storagequeue, 'log'):
            with storagequeue.StorageQueue(lambda: self.make_backend(), CONCURRENCY) as sq:
                p1 = storagequeue.PutOperation('test1', 'data')
                g1 = storagequeue.GetOperation('test1')
                g2 = storagequeue.GetOperation('test2')

                sq.enqueue(p1)
                sq.enqueue(g1)
                sq.enqueue(g2)

                self.assertRaises(storagequeue.OperationHasFailed, sq.wait)

    def test_bad_delete_fail(self):
        with logging.FakeLogger(storagequeue, 'log'):
            with storagequeue.StorageQueue(lambda: self.make_backend(), CONCURRENCY) as sq:
                p1 = storagequeue.PutOperation('test1', 'data')
                d1 = storagequeue.GetOperation('test1')
                d2 = storagequeue.GetOperation('test1')

                sq.enqueue(p1)
                sq.enqueue(d1)
                sq.enqueue(d2)

                self.assertRaises(storagequeue.OperationHasFailed, sq.wait)
    
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
