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

import errno
import os
import os.path
import shutil
import stat
import tempfile

import shastity.metadata as metadata

class StaleTemporaryDirectory(Exception):
    '''Raised to indicate that an attempt to use a stale (cleaned up)
    temporary directory was detected.'''
    pass

class TemporaryDirectory(object):
    '''An automatically cleaning temporary directory. The preferred
    use is with the 'with' statement, but calling code may also
    close() it explicitly. It will also close on GC.

    Most users will only be interested in the 'path' attribute of a
    temporary directory object.

    @ivar fs The file system with which the temporary directory is associated.
    @ivar path The path to the temporary directory.'''
    def __init__(self, fs, path):
        assert isinstance(fs, FileSystem)

        self.__fs = fs
        self.__path = path
        self.__stale = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if not self.__stale:
            self.__stale = True
            self.__fs.rmtree(self.__path)

    def __get_fs(self):
        if self.__stale:
            raise StaleTemporaryDirectory(self.__path)
        return self.__fs
        
    def __get_path(self):
        if self.__stale:
            raise StaleTemporaryDirectory(self.__path)
        return self.__path

    fs = property(__get_fs)
    path = property(__get_path)

class FileSystem(object):
    ''' Abstract base class of file systems (see module documentation
    for our definition of file system). This defines the interface to
    be implemented by file systems.

    Unless otherwise noted, methods with obvious POSIX counterparts
    will have matching semantics.

    In general, failure cases are those of POSIX.
    '''
    def mkdir(self, path):
        raise NotImplementedError

    def rmdir(self, path):
        raise NotImplementedError

    def unlink(self, path):
        raise NotImplementedError

    def symlink(self, src, dst):
        raise NotImplementedError

    def exists(self, path):
        return os.path.exists(path)

    def open(self, path, mode):
        raise NotImplementedError

    def is_symlink(self, path):
        '''@return Whether the given path is a symlink.'''
        raise NotImplementedError

    def is_dir(self, path):
        '''@return Whether the given path is a directory (or symlink pointing to one).'''
        raise NotImplementedError

    def listdir(self, path):
        '''@return List of filenames in the given directory.'''
        raise NotImplementedError

    def lstat(self, path):
        '''
        Stat the file at the given path, resutling in a FileMetaData object.

        @return A FileMetaData object.'''
        raise NotImplementedError

    def rmtree(self, path):
        '''Recursively delete the tree rooted at path (not following
        symlinks).'''
        # we implement this ourselves, rather than using
        # shutil.rmtree(), in order to have the same implementation
        # for regular fs and memory fs.
        if not self.is_symlink(path) and self.is_dir(path):
            for fname in self.listdir(path):
                self.rmtree(os.path.join(path, fname))
            self.rmdir(path)
        else:
            self.unlink(path)

    def mkdtemp(self, suffix=None):
        '''Atomically create/allocate a temporary directory and return
        its name.
        
        @note While similar, this is not identical to python's tempfile.mkdtemp().

        @param suffix: Suffix to apply to the allocated name, if supported.

        @return The absolute path of the temporary directory. '''
        raise NotImplementedError

    def tempdir(self, suffix=None):
        '''Allocate a temporary directory and return a
        TemporaryDirectory instance backed by this file system.

        @note This method has a default implementation in the abstract
              base class which is implemented in terms of mkdtemp().'''
        dirname = self.mkdtemp()
        return TemporaryDirectory(self, dirname)

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

    def is_symlink(self, path):
        return os.path.islink(path)

    def is_dir(self, path):
        return os.path.isdir(path)

    def listdir(self, path):
        '''@return List of filenames in the given directory.'''
        return os.listdir(path)

    def lstat(self, path):
        statinfo = os.lstat(path)
        
        props = dict()
        props['is_directory']        = stat.S_ISDIR(statinfo.st_mode)
        props['is_character_device'] = stat.S_ISCHR(statinfo.st_mode)
        props['is_block_device']     = stat.S_ISBLK(statinfo.st_mode)
        props['is_regular']          = stat.S_ISREG(statinfo.st_mode)
        props['is_fifo']             = stat.S_ISFIFO(statinfo.st_mode)
        props['is_symlink']          = stat.S_ISLNK(statinfo.st_mode)
        if props['is_symlink']:
            props['symlink_value']   = os.readlink(path)
        # TODO: socket?

        props['is_setuid']           = (statinfo.st_mode & stat.S_ISUID) == stat.S_ISUID
        props['is_setgid']           = (statinfo.st_mode & stat.S_ISGID) == stat.S_ISGID
        props['is_sticky']           = (statinfo.st_mode & stat.S_ISVTX) == stat.S_ISVTX

        props['user_read']           = (statinfo.st_mode & stat.S_IRUSR) == stat.S_IRUSR
        props['user_write']          = (statinfo.st_mode & stat.S_IWUSR) == stat.S_IWUSR
        props['user_execute']        = (statinfo.st_mode & stat.S_IXUSR) == stat.S_IXUSR
        props['group_read']          = (statinfo.st_mode & stat.S_IRGRP) == stat.S_IRGRP
        props['group_write']         = (statinfo.st_mode & stat.S_IWGRP) == stat.S_IWGRP
        props['group_execute']       = (statinfo.st_mode & stat.S_IXGRP) == stat.S_IXGRP
        props['other_read']          = (statinfo.st_mode & stat.S_IROTH) == stat.S_IROTH
        props['other_write']         = (statinfo.st_mode & stat.S_IWOTH) == stat.S_IWOTH
        props['other_execute']        = (statinfo.st_mode & stat.S_IXOTH) == stat.S_IXOTH

        props['uid']                 = statinfo[stat.ST_UID]
        props['gid']                 = statinfo[stat.ST_GID]
        props['size']                = statinfo[stat.ST_SIZE]
        props['atime']               = statinfo[stat.ST_ATIME]
        props['mtime']               = statinfo[stat.ST_MTIME]
        props['ctime']               = statinfo[stat.ST_CTIME]

        return metadata.FileMetaData(props=props)

    def mkdtemp(self, suffix=None):
        # mkdtemp differentiates between None and no parameter
        return tempfile.mkdtemp(suffix=('' if suffix is None else suffix))

# typical rwxr-xr-x default
_default_metadata = metadata.FileMetaData(props=dict(is_directory=False,
                                                     is_regular=False,
                                                     is_symlink=False,
                                                     is_block_device=False,
                                                     is_character_device=False,
                                                     is_fifo=False,
                                                     user_read=True,
                                                     user_write=True,
                                                     user_execute=True,
                                                     group_read=True,
                                                     group_write=False,
                                                     group_execute=True,
                                                     other_read=True,
                                                     other_write=False,
                                                     other_execute=True,
                                                     is_setuid=False,
                                                     is_setgid=False,
                                                     is_sticky=False,
                                                     uid=1,
                                                     gid=1,
                                                     size=0,
                                                     atime=5,
                                                     mtime=5,
                                                     ctime=5))

class MemoryDirectory:
    def __init__(self, parent):
        self.parent = parent
        self.entries = dict()
        self.metadata = metadata.FileMetaData(props=dict(is_directory=True),
                                              other=_default_metadata)

    def __getitem__(self, fname):
        if not fname in self.entries:
            raise OSError(errno.ENOENT, 'file not found')

        return self.entries[fname]

    def __contains__(self, fname):
        return fname in self.entries

    def lstat(self):
        return self.metadata

    def root(self):
        if self.parent:
            return self.parent.root()
        else:
            return self

    def lookup(self, comps, no_follow=False):
        if comps:
            if comps[0] == '/':
                return self.root().lookup(comps[1:], no_follow=no_follow)
            elif comps[0] in self.entries:
                # we don't recurse for non-directories mainly because
                # symlinks don't know their parent
                entry = self.entries[comps[0]]
                if isinstance(entry, MemoryDirectory):
                    return entry.lookup(comps[1:], no_follow=no_follow)
                elif isinstance(entry, MemoryFile):
                    if len(comps) > 1:
                        raise OSError(errno.ENOTDIR, 'not a directory')
                    else:
                        return entry
                elif isinstance(entry, MemorySymlink):
                    if no_follow:
                        if len(comps) == 1: # last component, we're done
                            return self
                        else:
                            raise AssertionError('no_follow, but request demanded follow (comps = %s)'
                                                 '' % (comps,))
                    else:
                        # ask symlink to resolve itself relative to us
                        return entry.resolve(self)
                else:
                    raise AssertionError('this code should not be reachable')
            else:
                raise OSError(errno.ENOENT, 'file not found')
        else:
            return self

    def is_empty(self):
        return not self.entries

    def is_dir(self):
        return True
    
    def is_symlink(self):
        return False

    def listdir(self):
        return self.entries.keys()
    
    def deparent(self):
        self.parent = None

    def mkdir(self, name):
        if name in self.entries:
            raise OSError(errno.EEXIST, 'file exists')
        self.entries[name] = MemoryDirectory(parent=self)

    def rmdir(self, name):
        if name not in self.entries:
            raise OSError(errno.ENOENT, 'file not found')
        
        if not isinstance(self.entries[name], MemoryDirectory):
            raise OSError(errno.ENOTDIR, 'not a directory')

        if not self.entries[name].is_empty():
            raise OSError(errno.ENOTEMPTY, 'directory not empty')
        
        del(self.entries[name])

    def exists(self, name):
        if not name in self.entries:
            return False

        entry = self.entries[name]
        if isinstance(entry, MemorySymlink):
            try:
                entry.resolve(self)
                return True
            except OSError, e:
                if e.errno == errno.ENOENT:
                    return False
                raise
        else:
            return True

    def link(self, memfile, name):
        if name in self.entries:
            raise OSError(errno.EEXIST, 'file exists - cannot link by that name')

        self.entries[name] = memfile

    def symlink(self, linkcomps, name):
        if name in self.entries:
            raise OSError(errno.EEXIST, 'file exists')

        self.entries[name] = MemorySymlink(linkcomps)
    
    def unlink(self, name):
        if not name in self.entries:
            raise OSError(errno.ENOENT, 'file not found')

        entry = self.entries[name]

        if isinstance(entry, MemoryDirectory):
            raise OSError(errno.EISDIR, 'cannot unlink directory - use rmdir()')
        elif isinstance(entry, MemorySymlink):
            del(self.entries[name])
        elif isinstance(entry, MemoryFile):
            del(self.entries[name])
        else:
            raise AssertionError('unknown entry type %s' % (entry.__class__,))

class MemorySymlink:
    def __init__(self, dest):
        '''@param dest: list (starts with . or /) of components'''
        self.dest = dest
        self.metadata = metadata.FileMetaData(props=dict(is_symlink=True,
                                                         symlink_value=self.readlink()),
                                              other=_default_metadata)

    def is_dir(self):
        return False

    def is_symlink(self):
        return True
    
    def lstat(self):
        return self.metadata

    def resolve(self, reldir):
        '''Resolve this symlink relative to the given directory.'''
        if self.dest[0] == '/':
            next_node = reldir.root()
        elif self.dest[0] == '.':
            next_node = reldir
        elif self.dest[0] == '..':
            next_node = reldir.parent
            if not next_node:
                raise OSError(errno.ENOENT, 'file not found (symlink past root node)')
        else:
            raise AssertionError('bug - bad start of symlink')

        return next_node.lookup(self.dest[1:])

    def readlink(self):
        return reduce(os.path.join, self.dest, '')

class MemoryFile:
    def __init__(self):
        self.contents = ''
        self.metadata = metadata.FileMetaData(props=dict(is_regular=True),
                                              other=_default_metadata)

    def is_dir(self):
        return False

    def is_symlink(self):
        return False

    def lstat(self):
        return self.metadata    

class OpenMode:
    '''Trivial helper to interpret fopen() style modestrings.

    @ivar reading_allowed
    @ivar writing_allowed
    @ivar truncate_on_open
    @ivar create_on_open
    @ivar at_beginning
    @ivar at_end
    @ivar append_only'''
    def __init__(self, modestring):
        if modestring == 'r':
            self.reading_allowed = True
            self.writing_allowed = False
            self.truncate_on_open = False
            self.create_on_open = False
            self.at_beginning = True
            self.at_end = not self.at_beginning
            self.append_only = False
        elif modestring == 'r+':
            self.reading_allowed = True
            self.writing_allowed = True
            self.truncate_on_open = False
            self.create_on_open = False
            self.at_beginning = True
            self.at_end = not self.at_beginning
            self.append_only = False
        elif modestring == 'w':
            self.reading_allowed = False
            self.writing_allowed = True
            self.truncate_on_open = True
            self.create_on_open = True
            self.at_beginning = True
            self.at_end = not self.at_beginning
            self.append_only = False
        elif modestring == 'w+':
            self.reading_allowed = True
            self.writing_allowed = True
            self.truncate_on_open = True
            self.create_on_open = True
            self.at_beginning = True
            self.at_end = not self.at_beginning
            self.append_only = False
        elif modestring == 'a':
            self.reading_allowed = False
            self.writing_allowed = True
            self.truncate_on_open = False
            self.create_on_open = True
            self.at_beginning = False
            self.at_end = not self.at_beginning
            self.append_only = True
        elif modestring == 'a+':
            self.reading_allowed = True
            self.writing_allowed = True
            self.truncate_on_open = False
            self.create_on_open = True
            self.at_beginning = False
            self.at_end = not self.at_beginning
            self.append_only = True
        else:
            raise AssertionError('invalid mode string: %s' % (modestring,))

class MemoryFileObject:
    '''File-like object for the memory file system.

    @note We do not implement sparse file semantics.
    @note Several methods remain unimplemented.
    @note We are not efficient in general, just functional.'''
    def __init__(self, memfile, mode):
        '''@type mode OpenMode'''
        self.memfile = memfile
        self.mode = mode

        if self.mode.truncate_on_open:
            self.memfile.contents = ''
        self.pos = 0 if self.mode.at_beginning else len(memfile.contents)
        
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        pass # nothing to be done

    def flush(self):
        pass

    def fileno(self):
        # file descriptors don't make sense for us; but we want calls
        # to fileno() to not fail such that filenos can be given to
        # e.g. fsync(). however, we also do not want to give something
        # out that could possibly be construed as a valid file
        # descriptor (that would be inviting accidentally using such a
        # thing for calls to something other than the memory file
        # system).
        return None

    def isatty(self):
        return False

    def next(self):
        raise NotImplementedError('next() not yet implemented for memory fs')

    def read(self, size=-1):
        if size == 0:
            return ''
        elif size < 0:
            ret = self.memfile.contents[self.pos:]
            self.pos += len(ret)
            return ret
        else:
            ret = self.memfile.contents[self.pos:self.pos + size]
            self.pos += len(ret)
            return ret

    def readline(self, size=-1):
        # \r?
        if size <= 0:
            size = len(self.memfile.contents) - self.pos
        nlpos = self.memfile.contents.find('\n', self.pos, self.pos + size)

        if nlpos == -1:
            ret = self.memfile.contents[self.pos, self.pos + size]
            self.pos += len(ret)
            return ret
        else:
            ret = self.memfile.contents[self.pos, nlpos + 1]
            self.pos += len(ret)
            return ret

    def readlines(self, sizehint=None):
        raise NotImplementedError

    def xreadlines(self):
        raise NotImplementedError

    def seek(self, offset, whence=os.SEEK_SET):
        raise NotImplementedError

    def tell(self):
        raise NotImplementedError

    def truncate(self, size=0):
        self.memfile.contents = self.memfile.contents[0:size + 1]
        
    def write(self, str):
        self.memfile.contents = self.memfile.contents[0:self.pos + 1] + str + self.memfile.contents[self.pos + 1:]

    def writelines(self, sequence):
        raise NotImplementedError
            
class MemoryFileSystem(FileSystem):
    '''A simple in-memory file system primarily intended for unit testing.

    Implementation notes
    ====================

    TODO: talk about permissions
    TODO: talk about concurrency'''

    def __init__(self):
        # Internally we use MemoryDirectory, MemorySymlink, MemoryFile
        # and MemoryFileObject to accomplish our goal.
        # 
        # We are mostly responsible for converting between string
        # based paths (a/b/c) to component based paths (['a', 'b',
        # 'c']) and implementing logic which is beyond the scope of
        # individual instances of the classes mentioned.

        self.__root = MemoryDirectory(parent=None)
        self.__root.link(MemoryDirectory(parent=self.__root), 'tmp')

        self.__tmp_count = 0   # Used to allocate unique temp names
        self.__cwd = self.__root

    def __split_slash_agnostically(self, path):
        directory, file = os.path.split(path)
        if not file:
            directory, file = os.path.split(directory)

        assert directory, 'directory expected on input path %s' % (path,)
        assert file, 'file expected on input path %s' % (file,)

        return (directory, file)

    def __tokenize(self, path):
        if len(path) > 1 and path.endswith('/'):
            path = path[0:len(path) - 1]

        while path.find('//') != -1:
            path.replace('//', '/')

        if path.startswith('/'):
            if len(path) > 1:
                return ['/'] + path[1:].split('/')
            else:
                return ['/']
        else:
            return path.split('/')

    def __lookup(self, path, no_follow=False):
        # todo: abs vs. rel
        return self.__root.lookup(self.__tokenize(path), no_follow=no_follow)

    def mkdir(self, path):
        dname, fname = self.__split_slash_agnostically(path)
        d = self.__lookup(dname)

        if not d.is_dir():
            raise OSError(errno.ENOTDIR, 'not a directory (%s)' % (directory,))

        d.mkdir(fname)

    def rmdir(self, path):
        if path == '/':
            raise OSError(errno.EINVAL, 'invalid argument - cannot rmdir /')

        dname, fname = self.__split_slash_agnostically(path)
        d = self.__lookup(dname)

        d.rmdir(fname)

    def unlink(self, path):
        if path == '/':
            raise OSError(errno.EINVAL, 'invalid argument - cannot unlink /')

        dname, fname = self.__split_slash_agnostically(path)
        d = self.__lookup(dname)

        d.unlink(fname)

    def symlink(self, src, dst):
        dname, fname = self.__split_slash_agnostically(dst)
        d = self.__lookup(dname)

        d.symlink(self.__tokenize(src), fname)

    def exists(self, path):
        try:
            self.__lookup(path)
            return True
        except OSError, e:
            if e.errno == errno.ENOENT:
                return False
            else:
                raise

    def open(self, path, modestring):
        mode = OpenMode(modestring)
        if mode.create_on_open:
            if not self.exists(path):
                dname, fname = self.__split_slash_agnostically(path)
                self.__lookup(dname).link(MemoryFile(), fname)
        return MemoryFileObject(self.__lookup(path), mode)

    def is_symlink(self, path):
        dname, fname = self.__split_slash_agnostically(path)
        d = self.__lookup(dname)

        if not d.is_dir():
            raise OSError(errno.EISDIR, 'is a directory')

        return d[fname].is_symlink()

    def is_dir(self, path):
        return self.__lookup(path).is_dir()

    def listdir(self, path):
        if not self.is_dir(path):
            raise OSError(errno.ENOTDIR, 'not a directory')

        return self.__lookup(path).listdir()

    def lstat(self, path):
        dname, fname = self.__split_slash_agnostically(path)
        d = self.__lookup(dname)

        if not d.is_dir():
            raise OSError(errno.EISDIR, 'is a directory')

        if not fname in d:
            raise OSError(errno.ENOENT, 'file not found')

        return d[fname].lstat()

    def mkdtemp(self, suffix=None):
        tmpname = 'tmp%s' % (str(self.__tmp_count),)
        self.__tmp_count += 1

        # we may legitimately collide since we blindly hope no one
        # created a matching file, or /tmp could be removed
        d = self.__lookup('/tmp')
        fullname = '%s%s' % (tmpname, ('-%s' % (suffix,)) if suffix else '')

        d.link(MemoryDirectory(parent=d), fullname)

        return '/tmp/%s' % (fullname,)

    def tempdir(self, suffix=None):
        return TemporaryDirectory(self, self.mkdtemp())
    
        
