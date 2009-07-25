# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.spencode as sp

class SpencodeTests(unittest.TestCase):

    def conv(self, s):
        encoded = sp.spencode(s)

        self.assertTrue(len(encoded) >= 2)
        self.assertTrue(encoded[0] == "'")
        self.assertTrue(encoded[len(encoded) - 1] == "'")

        for c in encoded[1:len(encoded) - 1]:
            if (not c in sp._safechars) and (c != '%'):
                raise AssertionError('unsafe non-%% character (%s) found in: %s '
                                     'encoded from %s' % (c, encoded, s))

        decoded = sp.spdecode(encoded)

        self.assertEqual(decoded, s)

    def test_manual(self):
        self.conv('test')
        self.conv("' test 'tost'\\.)*(!^*#%&*^&(*")
        self.conv('')

    def test_ascii_exhaustively(self):
        all_chars = ''.join([ chr(n) for n in xrange(0, 128) ])

        for length in xrange(0, 5):
            for pos in xrange(0, 128 - length):
                s = ''.join([ all_chars[pos + i] for i in xrange(0, length)  ])
                self.conv(s)
                
    def test_some_8bit(self):
        self.conv(u'åäöü')

    def test_byte_enc(self):
        all_bytes = ''.join([ chr(n) for n in xrange(0, 256) ])
        
        for b in all_bytes:
            self.assertEqual(b, sp._urldec(sp._urlenc(b)))

if __name__ == "__main__":
    unittest.main()
