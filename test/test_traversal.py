# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import errno
import os.path
import unittest

import shastity.filesystem as fs
import shastity.metadata as md
import shastity.traversal as traversal

class TraversalBaseCase(object):
    def setUp(self):
        self.fs = self.make_file_system() # provided by subclass

    def path(self, base, p):
        '''path('base', '/path/to/file') -> 'base/path/to/file', with portable / splitting'''
        return os.path.join(base, (reduce(os.path.join, [ comp for comp in p.split('/') if comp ])))

    def test_basic(self):
        with self.fs.tempdir() as tdir:
            lst = [ elt for elt in traversal.traverse(self.fs, tdir.path) ] 
            self.assertEqual(len(lst), 1)

    def test_directory_traversal(self):
        with self.fs.tempdir() as tdir:
            self.fs.mkdir(self.path(tdir.path, 'testdir'))
            self.fs.mkdir(self.path(tdir.path, 'testdir/subdir'))

            lst = [ elt for elt in traversal.traverse(self.fs, tdir.path) ] 
            self.assertEqual(len(lst), 3)

    def test_recursive_symlink(self):
        with self.fs.tempdir() as tdir:
            self.fs.mkdir(self.path(tdir.path, 'testdir'))
            self.fs.symlink(self.path(tdir.path, 'testdir'),
                            self.path(tdir.path, 'testdir/symlink_to_parent'))

            lst = [ elt for elt in traversal.traverse(self.fs, tdir.path) ] 
            self.assertEqual(len(lst), 3)
        

class LocalFileSystemTests(TraversalBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.LocalFileSystem()

class MemoryFileSystemTests(TraversalBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.MemoryFileSystem()

if __name__ == "__main__":
    unittest.main()
