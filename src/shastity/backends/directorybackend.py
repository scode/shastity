# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Local file system directory backend.
'''

from __future__ import absolute_import
from __future__ import with_statement

import os.path

import shastity.backend as backend
import shastity.logging as logging

log = logging.get_logger(__name__)

class DirectoryBackend(backend.Backend):
    '''Very simple file system directory based backend. Each file
    corresponds to a file in the directory (whose path is exactly
    identical to the backend identifier).

    @note The implementation of this backend, by design, goes straight
          to the file system rather than using our file system
          abstraction from shastity.filesystem.'''

    # prefix offiles that are internal to backend operations. we
    # disallow ever putting files by this name, we hide them on
    # listings, and we assume we can remove them at any time because
    # we own them. this scheme is technically a bit broken since it
    # will dis-allow certain names, but it's dead simple and will not
    # interfer with expected shastity operation - butif it does, it
    # will scream rather than silently fail.
    hidden_prefix = '__shastity_directory_backend.'

    def __init__(self, identifier):
        backend.Backend.__init__(self, identifier)
        
        self.__path = identifier # redundant but clearer

        if not os.path.exists(self.__path):
            log.notice('creating non-existent directory %s', self.__path)
            os.makedirs(self.__path)
        
        # clean up after previous crashes/failures
        files_to_clean = [ name for name in os.listdir(self.__path) if name.startswith(self.hidden_prefix) ]
        for fname in files_to_clean:
            log.warning('removing stale (post-crash/post-abort?) file %s', fname)
            os.unlink(os.path.join(self.__path, fname))

    def put(self, name, data):
        assert not name.startswith(self.hidden_prefix)

        log.info('putting %s (%d bytes)', name, len(data))

        fd, tmppath = tempfile.mkstemp(prefix=self.hidden_prefix, dir=self.__path, suffix=('-%s' % (name,)))
        try:
            assert tmppath.startswith(self.hidden_prefix)
            
            os.write(fd, data)
            
            # This fsync() is absolutely critical. Even if a user is
            # okay with loosing data on power outtage/crash, we
            # *CANNOT* just remove this fsync() because we risk not
            # just loosing data, but actually corrupting it if the
            # rename() is persisted prior to data we just wrote. If
            # future performance optimization is done it should be
            # done differently (e.g. batch:ed fsync():s).
            os.fsync(fd)

            os.rename(tmppath, os.path.join(self.__path, name))
        finally:
            os.close(fd)
            
    def get(self, name):
        assert not name.startswith(self.hidden_prefix)

        log.info('getting %s', name)

        with file(os.path.join(self.__path, name), 'r') as f:
            return f.read()

    def list(self):
        log.info('listing backend files')
        return [ name for name in os.listdir(self.__path) if not name.startswith(self.hidden_prefix) ]

    def delete(self, name):
        assert not name.startswith(self.hidden_prefix)


        log.info('deleting %s', name)

        os.unlink(os.path.join(self.__path, name))

        # unfortunately this unlink is not guaranteed to be
        # persistent. i am not sure what would be a *portable* way of
        # ensuring persistent unlink; but in any case an un-executed
        # delete is not dangerous to shastity internal consistency.

    def close(self):
        pass
    
