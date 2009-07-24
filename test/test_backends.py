# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.backend as backend

class BackendsBaseCase(object):
    def setUp(self):
        self.backend = self.make_backend() # provided by subclass

    def test_misc(self):
        pass

if __name__ == "__main__":
    unittest.main()
