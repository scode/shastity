# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Takes stream(s) of (path, metadata) and persists to backends.
'''

from __future__ import absolute_import
from __future__ import with_statement

import  os.path

import shastity.filesystem as filesystem
import shastity.logging as logging

log = logging.get_logger(__name__)

def persist_full(fs, traversal, basepath, storagequeue):
    '''
    @param fs: File system from which to read file contents.
    @param traversal: Generator producting (path, metadata) entries.
    @param basepath: Base path (prefix) of backup.
    @param storagequeue: Storage queue to which to write files contents.
    '''
    pass
