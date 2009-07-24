# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
File storage backend interface.
"""

class Backend(object):
    '''A storage backend. A backend is anything which allows four
    basic operations:

      - PUT files, by a given name and contents, to the backend.
      - GET files, by a given name, from the backend.
      - LIST files stored in the backend.
      - DELETE files stored in the backend.

    In general, due the way shastity stores data, backends are
    particularly sensitive to per-operation overheads when storing or
    getting small files. In other words, it is important that the
    backend be fast at storing and retrieving small files.

    Because it is anticipated that some backends may be fundamentally
    difficult to make efficient in this way, all backend:s should be
    implemented such that concurrent use of *distinct* (not the same)
    instances from multiple threads is safe (multi-threading *may* be
    an optimizing implemented at a future time, but regardless writing
    code like that is good practice anyway).

    Backends must be able to handle reasonably long file names. No
    effort is made to be compatible with legacy 8.3 file system
    conventions or similar; any such acrobatics would have to be
    implemented by a particular backend, taking great care to adher to
    the semantics mandaged by each call.

    All backend classes are expected to be possible to instantiate by
    giving them one parameter - the identifier.

    @ivar identifier The identifier given to the Backend constructor.'''
    def __init__(self, identifier):
        '''Instantiate the backend, storing the identifier. Expected
        to be called by sub-classes.

        @param identifier The identifying URL/name/path/etc of this
        backend.'''
        pass

    def put(self, name, data):
        raise NotImplementedError

    def get(self, name):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def delete(self, name):
        raise NotImplementedError
