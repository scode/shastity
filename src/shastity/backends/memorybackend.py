# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
In-memory backend.
'''

import shastity.backend as backend

class MemoryBackend(backend.Backend):
    '''Trivial in-memory backend that simply maps all operations to an
    internal dict. Obviously this does violate the supposed
    persistence guarantee of a backend; this is intended for unit
    testing purposes.'''
    def __init__(self, identifier, opts=dict()):
        backend.Backend.__init__(self, identifier, opts)

        self.__dict = dict()

    def exists(self):
        return True

    def create(self):
        pass # nothing to be done

    def put(self, name, data):
        self.__dict[name] = data

    def get(self, name):
        return self.__dict[name]

    def list(self):
        return self.__dict.keys()

    def delete(self, name):
        del(self.__dict[name])

    def close(self):
        pass
    
