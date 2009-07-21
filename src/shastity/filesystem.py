# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
Provide a thin wrapper around file system operations. Reasons for
doing this include:

  - It makes it easier to unit test code that depends on file system access
    because we can more easily write mock-ups.
  - File system operations are potentially platform sensetive, so it is nice to
    have them in one place.
  - File system operations are a "dangerous" part of shastity in the sense that
    they side-effect on the surrounding environment. It is nice to avoid having
    such things spread all over the place.

Because file system access is inherently destructive in nature (i.e.,
has side-effects) we comfortable module file systems as class
instances.

Note that our "file system" concept is not the same as that of an
operating system; to us, a file system is basically "files and
directories accessible by the process via the native system's API". We
do not intend to imply any specific knowledge about OS file system
mount points, types, or anything like that.
"""

from __future__ import absolute_import
from __future__ import with_statement

import os

class FileSystem(object):
    def mkdir(self, path):
        raise NotImplementedError

    def rmdir(self, path):
        raise NotImplementedError

    def unlink(self, path):
        raise NotImplementedError

    def symlink(self, src, dst):
        raise NotImplementedError

    def open(self, path, mode):
        raise NotImplementedError

class LocalFileSystem(FileSystem):
    def mkdir(self, path):
        os.mkdir(path)

    def rmdir(self, path):
        os.rmdir(path)

    def unlink(self, path):
        os.unlink(path)

    def symlink(self, src, dst):
        os.symlink(src, dst)

    def open(self, path, mode):
        return open(path, mode)
