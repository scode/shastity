# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
File storage backend interface.
"""

from __future__ import absolute_import
from __future__ import with_statement

from Crypto.Cipher import AES
import struct

import shastity.logging as logging
import shastity.hash as hash

log = logging.get_logger(__name__)

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

    Concurrency and thread-safety
    =============================

    Because it is anticipated that some backends may be fundamentally
    difficult to make efficient in this way, all backend:s should be
    implemented such that concurrent use of *distinct* (not the same)
    instances from multiple threads is safe. The only expect is
    exists() and create() which are specifically designed to be
    'administrative' commands and are not meant to be invoked in
    highly concurrent fashion; in particular these two operations are
    specifically expected to affect shared state.
    
    Backends can assume that when they receive put/get/delete/list
    requests, the backing storage has either been created some time
    prior to the instantiation of that backend, or it was created
    using that particular backend instance.

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

    Another important consideration is that regardless of consistency
    guarantee, a backend *must* honor the order of operations. For
    example, if shastity does:

      (1) PUT x
      (2) DELETE x
      (3) PUT x

    It would be broken behavior for (3) to fail due to a delayed (2).

    @ivar identifier The identifier given to the Backend constructor.'''
    def __init__(self, identifier, opts=dict()):
        '''Instantiate the backend, storing the identifier. Expected
        to be called by sub-classes.

        @param identifier The identifying URL/name/path/etc of this
        backend.'''
        
        self.identifier = identifier
        self.cryptoKey = None

        log.info('instantiating backend of type %s with identifier %s',
                 self.__class__.__name__, self.identifier)

    def setCryptoKey(self, cryptoKey):
        self.cryptoKey = hash.make_hasher('sha512')(cryptoKey)[1]        

    def encryptName(self, name):
        if not self.cryptoKey:
            return name
        crypt = AES.new(self.cryptoKey[:16], AES.MODE_CBC)
        s = struct.pack("!l", len(name)) + name
        if len(s) % 16:
            s = s + " " * (16 - len(s) % 16)
        ret = crypt.encrypt(s)
        return ''.join(["%.2x" % (ord(x)) for x in ret])

    def decryptFilename(self, cfn):
        if not self.cryptoKey:
            return cfn
        crypt = AES.new(self.cryptokey[:16], AES.MODE_CBC)
        s = ''.join([chr(int(x,16)) for x in re.findall('(..)', cfn)])
        dec = crypt.decrypt(s)
        l = struct.unpack("!l", dec[:4])[0]
        return dec[4:4+l]

    def __enter__(self):
        '''Returns self.'''
        return self

    def __exit__(self, *args, **kwargs):
        '''Calls self.close().'''
        self.close()

    def exists():
        ''' Checks whether backend storage exists. The definition of
        "exists" is up to the backend; some may not have such a
        concept at all, in which case it always exists.
        
        The main purpose for the exists()/create() interface is to
        allow shastity to initialize, if needed, storage prior to main
        operation (where multiple concurrent operations may occurr),
        saving backends from having to be safe w.r.t. concurrency when
        creating backing storage.

        @return Whether or not the backend storage exists.'''
        raise NotImplementedError

    def create():
        '''Create the necessary backend storage. Will only be called
        if exists() returned false. Contrary to put/get/delete/list(),
        this operation is expected to have side-effects on state that
        is shared between multiple instances of the backend, and need
        NOT be thread-safe.'''
        raise NotImplementedError

    def put(self, name, data):
        '''Put a file by the given name and contents into the store.

        The put operation must satisfy several characteristics:

          - The operation must atomically either succeed or not; the backend
            must guarantee that a half-finished or otherwise failed put operation
            will not cause a particially put files to be available and visible to
            subsequent list() or get().

          - When the put completes successfully, the file is considered to be written
            successfully and persistently (see consistency notes in class docs). In particular
            whichever put happens *last* must take presedence.

          - Duplicate put operations absolutely *must* be handled, *or* the backend's list() must
            be strictly up-to-date with respect to put():s.

        @type name string
        @param name The name of the file.

        @type data bytes
        @param data The contents of the file.'''
        raise NotImplementedError

    def get(self, name):
        '''Get the contents of the file by the given name.

        @type name string
        @param name The name of the file to get.
        
        @rtype bytes
        @return The contents of the file.'''
        raise NotImplementedError

    def list(self):
        '''Get a complete list of all files in the backend.

        @rtype list of strings
        @return List of file names.'''
        raise NotImplementedError

    def delete(self, name):
        '''Delete the given file in the backend.

        @type name string
        @param name Name of file to delete.'''
        raise NotImplementedError

    def close(self):
        '''Close the backend, releasing any resources it may
        occupy.'''
        pass
