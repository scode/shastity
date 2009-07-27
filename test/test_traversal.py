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

    def test_misc(self):
        pass

class LocalFileSystemTests(TraversalBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.LocalFileSystem()

class MemoryFileSystemTests(TraversalBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.MemoryFileSystem()

if __name__ == "__main__":
    unittest.main()
