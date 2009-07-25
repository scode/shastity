# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import errno
import os.path
import unittest

import shastity.metadata as metadata

class MetaDataTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_write_protection(self):
        md = metadata.FileMetaData()
        
        def assign_test():
            md.user_write = False
        self.assertRaises(AssertionError, assign_test)

    def test_init_assignment(self):
        for propname in metadata.FileMetaData.propnames:
            for boolval in [ True, False ]:
                propdic = dict()
                propdic[propname] = boolval

                self.assertEqual(getattr(metadata.FileMetaData(props=propdic), propname), boolval)

    def test_other_copy(self):
        for propname in metadata.FileMetaData.propnames:
            for boolval in [ True, False ]:
                propdic = dict()
                propdic[propname] = boolval

                self.assertEqual(getattr(metadata.FileMetaData(other=metadata.FileMetaData(props=propdic)), propname), boolval)

if __name__ == "__main__":
    unittest.main()
