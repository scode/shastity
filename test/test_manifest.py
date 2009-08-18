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
import shastity.hash as hash
import shastity.logging as logging
import shastity.manifest as manifest
import shastity.metadata as md
import shastity.persistence as persistence
import shastity.storagequeue as storagequeue
import shastity.traversal as traversal

log = logging.get_logger(__name__)

class ManifestBaseCase(object):
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
        with self.make_backend() as b:
            def make_entry(n, contents):
                return ('%d' % (n,), md.FileMetaData.from_string('-rwxr-xr-x 5 6 7 8 9 10'), [('sha512', 'abcd')])

            entries_in = [ make_entry(n, 'contents'.join([ unicode(m) for m in xrange(0, n)])) for n in xrange(0, 100) ]
            
            manifest.write_manifest(b, 'test_manifest', entries_in)
            entries_out = [ entry for entry in manifest.read_manifest(b, 'test_manifest') ]

            #print b.get('test_manifest')

            self.assertEqual(manifest.list_manifests(b), [ 'test_manifest' ])
            manifest.delete_manifest(b, 'test_manifest')
            self.assertEqual(manifest.list_manifests(b), [])

            def to_comparable(entry):
                path, md, algos = entry

                return (path, md.to_string(), algos)

            self.assertEqual([ to_comparable(entry) for entry in entries_in ],
                             [ to_comparable(entry) for entry in entries_out])

class MemoryTests(ManifestBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.MemoryFileSystem()
    
    def make_backend(self):
        return memorybackend.MemoryBackend('memory')
        
class LocalFileSystemTests(ManifestBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.LocalFileSystem()

    def make_backend(self):
        return directorybackend.DirectoryBackend(self.tempdir)

if os.getenv('SHASTITY_UNITTEST_S3_BUCKET') != None:
    class S3Tests(ManifestBaseCase, unittest.TestCase):
        def make_file_system(self):
            return fs.LocalFileSystem()
    
        def make_backend(self):
            return s3backend.S3Backend(os.getenv('SHASTITY_UNITTEST_S3_BUCKET')) # todo
    
if __name__ == "__main__":
    unittest.main()
