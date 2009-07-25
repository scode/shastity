# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import shutil
import tempfile
import unittest

import shastity.backend as backend
import shastity.backends.memorybackend as memorybackend
import shastity.backends.directorybackend as directorybackend
import shastity.logging as logging

log = logging.get_logger(__name__)

PREFIX = 'shastity_unittest_'

def prefix(name):
    '''Trivial convenience function for constructing a PREFIX:ed filename.'''
    return PREFIX + name

class BackendsBaseCase(object):
    '''Base class for backend unit tests. Subclasses need to implement
    make_backend() (and possibly backend specific tests).'''

    def setUp(self):
        self.backend = self.make_backend() # provided by subclass

        # We do not assume the backend is empty at the time the test
        # starts, but we do assume that we can put, get and delete any
        # file beginning with PREFIX. In order to ensure we can re-run
        # tests in an idempotent fashion, we clean up pre-existing
        # files of tests first.
        fnames = self.get_testfiles()

        for fname in fnames:
            self.backend.delete(fname)

    def get_testfiles(self):
        return [ name for name in self.backend.list() if name.startswith(PREFIX)]

    def test_basic(self):
        self.assertEqual(self.get_testfiles(), [])

        # put/get
        self.backend.put(prefix('test'), 'data')
        self.assertEqual(self.backend.get(prefix('test')), 'data')
        
        # list
        self.assertEqual(len(self.get_testfiles()), 1)
        self.assertEqual(self.get_testfiles()[0], prefix('test'))

        # delete
        self.backend.delete(prefix('test'))
        self.assertEqual(len(self.get_testfiles()), 0)

    def test_empty_file(self):
        self.backend.put(prefix('emptytest'), '')
        self.assertEqual(self.backend.get(prefix('emptytest')), '')
        self.backend.delete(prefix('emptytest'))

    def test_largish_file(self):
        kbyte = ''.join(['x' for nothing in xrange(0, 1024)])
        mbyte = ''.join([ kbyte for nothing in xrange(0, 1024)])
        self.backend.put(prefix('largetest'),  mbyte)
        self.assertEqual(self.backend.get(prefix('largetest')), mbyte)
        self.backend.delete(prefix('largetest'))

    def test_long_filename(self):
        lname = 'ldjfajfldjflasdjfklsdjfklasdjfldjfljsdljfasdjfklasdjfklasdjflasdjklfasdjklffweruasfasdfweruwaourweourwepoqurweipoqurqwepourqweiporewr'
        self.backend.put(prefix(lname), 'data')
        self.assertEqual(self.backend.get(prefix(lname)), 'data')
        self.assertTrue(prefix(lname) in self.get_testfiles())

    def test_several_files(self):
        fnames = [ prefix('fnumber_%d' % (n,)) for n in xrange(0, 100) ]
        for fname in fnames:
            self.backend.put(prefix(fname), fname)
        flist = self.backend.list()
        for fname in fnames:
            self.assertTrue(prefix(fname) in flist)
            self.assertEqual(self.backend.get(prefix(fname)), fname)

    def test_funny_data(self):
        # make sure we do not have scrambling of certain byte values,
        # truncate on zeroes, or similar
        all_bytes = ''.join([ chr(n) for n in xrange(0, 255) ])

        self.backend.put(prefix('funnydata'), all_bytes)
        self.assertEqual(self.backend.get(prefix('funnydata')), all_bytes)

class MemoryBackendTests(BackendsBaseCase, unittest.TestCase):
    def make_backend(self):
        return memorybackend.MemoryBackend('memory')

class DirectoryBackendTests(BackendsBaseCase, unittest.TestCase):
    def make_backend(self):
        return directorybackend.DirectoryBackend(self.tempdir)

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(suffix='-shastity_directory_backend_unittest')
        log.debug('using temporary directory %s', self.tempdir)

        BackendsBaseCase.setUp(self)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

if __name__ == "__main__":
    unittest.main()
