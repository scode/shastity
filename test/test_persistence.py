# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import errno
import os.path
import shutil
import tempfile
import unittest

import shastity.backends.directorybackend as directorybackend
import shastity.backends.memorybackend as memorybackend
import shastity.filesystem as fs
import shastity.logging as logging
import shastity.metadata as md
import shastity.persistence as persistence
import shastity.storagequeue as storagequeue
import shastity.traversal as traversal

log = logging.get_logger(__name__)

CONCURRENCY = 10

class PersistenceBaseCase(object):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp(suffix='-shastity_directory_backend_unittest')
        log.debug('using temporary directory %s', self.tempdir)

        self.fs = self.make_file_system()  # provided by subclass
        self.backend = self.make_backend() # provided by subclass

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def path(self, base, p):
        '''path('base', '/path/to/file') -> 'base/path/to/file', with portable / splitting'''
        return os.path.join(base, (reduce(os.path.join, [ comp for comp in p.split('/') if comp ])))

    def test_basic(self):
        with storagequeue.StorageQueue(lambda: self.make_backend(), CONCURRENCY) as sq:
            with self.fs.tempdir() as tdir:
                # populate
                self.fs.mkdir(self.path(tdir.path, 'testdir'))
                self.fs.open(self.path(tdir.path, 'testdir/testfile'), 'a').close()
                with self.fs.open(self.path(tdir.path, 'testdir/testfile2'), 'a') as f:
                    f.write('this is the body of testfile2')
                self.fs.symlink(self.path(tdir.path, 'testdir/testfile2'),
                                self.path(tdir.path, 'testdir/testfile2-symlink'))

                traverser = traversal.traverse(self.fs, tdir.path)
                for path, meta, hashes in persistence.persist(self.fs, traverser, None, tdir.path, sq):
                    pass
                    #print meta.to_string() + ' ' + path + ' ' + unicode(hashes)

class MemoryTests(PersistenceBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.MemoryFileSystem()
    
    def make_backend(self):
        return memorybackend.MemoryBackend('memory')
        
class LocalFileSystemTests(PersistenceBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.LocalFileSystem()

    def make_backend(self):
        return directorybackend.DirectoryBackend(self.tempdir)

if os.getenv('SHASTITY_UNITTEST_S3_BUCKET') != None:
    class S3Tests(PersistenceBaseCase, unittest.TestCase):
        def make_file_system(self):
            return fs.LocalFileSystem()
    
        def make_backend(self):
            return s3backend.S3Backend(os.getenv('SHASTITY_UNITTEST_S3_BUCKET')) # todo
    
if __name__ == "__main__":
    unittest.main()
