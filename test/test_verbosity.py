# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.config as config
import shastity.logging as logging
import shastity.verbosity as verbosity

class VerbosityTests(unittest.TestCase):
    def test_to_level(self):
        verbosity.to_level(5)
        self.assertRaises(verbosity.InvalidVerbosityLevel,
                          lambda: verbosity.to_level(-5))

    def test_to_verbosity(self):
        def l(name):
            return verbosity.to_verbosity(getattr(logging, name))

        self.assertTrue(l('DEBUG') > l('INFO'))
        self.assertTrue(l('INFO') > l('NOTICE'))
        self.assertTrue(l('NOTICE') > l('WARNING'))
        self.assertTrue(l('WARNING') > l('ERROR'))
        self.assertTrue(l('ERROR') > l('CRITICAL'))

    def test_both(self):
        def tstlvl(lvl):
            self.assertEqual(lvl, verbosity.to_level(verbosity.to_verbosity(lvl)))

        tstlvl(logging.DEBUG)
        tstlvl(logging.INFO)
        tstlvl(logging.NOTICE)
        tstlvl(logging.WARNING)
        tstlvl(logging.ERROR)
        tstlvl(logging.CRITICAL)

if __name__ == '__main__':
    unittest.main()
