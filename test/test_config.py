# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.config as config

class ConfigTests(unittest.TestCase):
    def test_naming(self):
        self.assertEqual(config.StringOption('long-name', 'l').name(), 'long-name')
        self.assertEqual(config.StringOption('long-name', 'l').short_name(), 'l')

    def test_required(self):
        self.assertRaises(config.RequiredOptionMissingError,
                          lambda: config.StringOption('testname').get_required())
        self.assertEqual('test', config.StringOption('testname').parse('test').get_required())

    def test_string_option(self):
        config.StringOption('testname').parse('test')
        self.assertRaises(config.BadOptionValueType, lambda: config.StringOption('testname').parse(5))

    def test_int_option(self):
        config.IntOption('testname').parse(5)
        config.IntOption('testname').parse('5')
        self.assertRaises(config.BadOptionValueType, lambda: config.IntOption('testname').set('5'))

if __name__ == '__main__':
    unittest.main()
