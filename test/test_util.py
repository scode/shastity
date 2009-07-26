# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.util as util

class UtilTests(unittest.TestCase):

    def test_traceback(self):
        # we don't really test that the output looks okay, but rather
        # that it runs correctly. unlikely to be changed often anyway;
        # but more likely that some re-shuffling breaks imports, or
        # some python version has some incompatible change, etc.
        try:
            raise AssertionError('test')
        except:
            util.current_traceback()
            
if __name__ == "__main__":
    unittest.main()
