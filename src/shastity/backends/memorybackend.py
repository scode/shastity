# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
In-memory backend.
'''

from __future__ import absolute_import
from __future__ import with_statement

import random
import threading
import time

import shastity.backend as backend

_dict = dict()
_lock = threading.Lock()

class MemoryBackend(backend.Backend):
    '''Trivial in-memory backend that simply maps all operations to an
    internal dict. Obviously this does violate the supposed
    persistence guarantee of a backend; this is intended for unit
    testing purposes.

    It supports an option 'max_fake_delay' whose value is the number
    of seconds between 0 and which each operation will spend time im
    time.sleep(). This is intended, again, for unit testing purposes
    in order to try to trigger various timing dependent cases in a
    non-deterministic fashion.

    In order to simulate external storage that is shared between
    instances, it keeps thread-safe access to an instance independent
    shared dict for storage.'''
    def __init__(self, identifier, opts=dict()):
        backend.Backend.__init__(self, identifier, opts)

        self.__max_fake_delay = float(opts.get('max_fake_delay', 0.0))

    def __delay(self):
        if self.__max_fake_delay > 0.0:
            time.sleep(self.__max_fake_delay * random.random())

    def exists(self):
        return True

    def create(self):
        pass # nothing to be done

    def put(self, name, data):
        self.__delay()

        global _dict
        global _lock
        with _lock:
            _dict[name] = data

    def get(self, name):
        self.__delay()

        global _dict
        global _lock
        with _lock:
            return _dict[name]

    def list(self):
        self.__delay()

        global _dict
        global _lock
        with _lock:
            return _dict.keys()

    def delete(self, name):
        self.__delay()

        global _dict
        global _lock
        with _lock:
            del(_dict[name])

    def close(self):
        self.__delay()
    
