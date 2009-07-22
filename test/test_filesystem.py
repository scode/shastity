# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import errno
import unittest

import shastity.filesystem as fs

class FileSystemBaseCase(object):
    def setUp(self):
        self.fs = self.make_file_system() # provided by subclass

    def assertOSError(self, errno, fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
            raise AssertionError('expected OSError with errno %d; got no OSError at all' % (errno,))
        except OSError, e:
            self.assertTrue(e.errno == errno, 'errno %d expected, got %d' % (errno, e.errno))
        
    def test_tempdir(self):
        with self.fs.tempdir() as tdir:
            tpath = tdir.path
            self.assertTrue(self.fs.exists(tdir.path), 'tempdir should exist')

            self.assertOSError(errno.EEXIST, self.fs.mkdir, tdir.path)
            
        self.assertFalse(self.fs.exists(tpath), 'tempdir should be removed')

class LocalFileSystemTests(FileSystemBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.LocalFileSystem()

if __name__ == "__main__":
    unittest.main()
