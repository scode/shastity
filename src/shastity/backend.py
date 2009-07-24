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

    All backend classes are expected to be possible to instantiate by
    giving them one parameter - the identifier.

    Performance
    ===========

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

    Block/file sizes
    ================

    A fundamental assumption of shastity is that the block size used
    for file I/O will be "reasonably small"; thus backends can assume
    that data being put and gotten to/from the store will fit
    comfortably in RAM, and that it is okay to perhaps make a copy of
    a block of data and otherwise treat is as a medium-to-large piece
    of data, rather than a *huge* piece of data. This is an assumption
    that is part of the public interface of shastity and something we
    communicate to the user.

    Making this assumptions goes to simplicity of interface and
    implementation; there is no need to have elaborate logic for
    streaming very large files in a reliable fashion.

    File name restrictions
    ======================

    Backends must be able to handle reasonably long file names. No
    effort is made to be compatible with legacy 8.3 file system
    conventions or similar; any such acrobatics would have to be
    implemented by a particular backend, taking great care to adher to
    the semantics mandaged by each call.

    Consistency guarantees
    ======================

    From the perspective of the rest of shastity, backend put() and
    delete() operations are considered persistent and durable. If a
    backend does not satisfy that requirement, it needs to communiate
    its consistency guarantee to the user via documentation, and needs
    to consider the possible cases. For example in the case of an
    eventually consistent S3 store, there is no internal consistency
    problem sooner or later the result of a PUT will become available.

    In general shastity uses the backend in such a way that internal
    inconsistencies do not occurr, but of course any delays or loss of
    data will be propagated to the user. For example::

      - A delayed effect of put() will have no negative effects other
        than the user having to wait for said delay before being able
        to restore the data - just as long as the backend is
        internally correct and is able to handle, for example, two
        successive put():s of the same file, ensuring the "newest"
        put() operation always takes presedence.

      - A delayed delete() will simply cause old data to be visible for
        a bit longer. No internal logic will break in shastity; again as long
        as the backend works internally.

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
