# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.config as config
import shastity.verbosity as verbosity

class VerbosityTests(unittest.TestCase):
    def test_to_level(self):
        verbosity.to_level(5)
        self.assertRaises(verbosity.InvalidVerbosityLevel,
                          lambda: verbosity.to_level(-5))

if __name__ == '__main__':
    unittest.main()
