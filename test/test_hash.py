# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.hash as hash

class HashTests(unittest.TestCase):
    def test_generic(self):
        for algo in hash._our_supported_hashlib_algos:
            h = hash.make_hasher(algo)
            self.assertTrue(h is not None, 'should have been given a hasher')
            self.assertTrue(callable(h), 'hasher should be callable')
            name, digest = h('test data')
            self.assertEqual(name, algo)
            # PY3-TODO
            self.assertTrue(isinstance(digest, str) or isinstance(digest, unicode), 'digest does not look like one')

            h('')

    def test_sha512(self):
        sha512 = hash.make_hasher('sha512')
        self.assertEqual(sha512('test'), ('sha512', 'ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db27ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff'))

    def test_badalgo(self):
        def fail():
            hash.make_hasher('random non-existent algo')
        self.assertRaises(hash.UnsupportedHashAlgorithm, fail)

if __name__ == "__main__":
    unittest.main()
