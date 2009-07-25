# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

# the order of these tests should be kept roughly in in order of
# most-self-contained-first and
# least-dependent-on-other-things-first. the intent is to increase the
# chances that the first unit test that breaks is indicative of where
# the bug is.
test_names = [ 'logging',
               'hash',
               'spencode',
               'metadata',
               'filesystem',
               'backends' ]

if __name__ == "__main__":
   suite = unittest.defaultTestLoader.loadTestsFromNames([ 'test_%s' % (tn,) for tn in test_names])
   unittest.TextTestRunner(verbosity=2).run(suite)
