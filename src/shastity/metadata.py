# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
File meta data handling.
'''

def mode_to_str(propdict):
    '''Internal helper similar to strmode(3). Produces
    'drwxr-xr-x' style (like ls -l) mode strings from the
    permission/sticky/setuid attributes.'''
    d = propdict

    chars = [] # list of characters later to be joined into string

    if d['is_regular']:
        chars.append('-')
    elif d['is_block_device']:
        chars.append('b')
    elif d['is_character_device']:
        chars.append('c')
    elif d['is_directory']:
        chars.append('d')
    elif d['is_symlink']:
        chars.append('l')
    elif d['is_fifo']:
        chars.append('p')
    else:
        raise AssertionError('should not be reachable')

    if d['user_read']:
        chars.append('r')
    else:
        chars.append('-')

    if d['user_write']:
        chars.append('w')
    else:
        chars.append('-')

    if d['user_execute']:
        if d['is_setuid']:
            chars.append('s')
        else:
            chars.append('x')
    else:
        if d['is_setuid']:
            chars.append('S')
        else:
            chars.append('-')
        
    if d['group_read']:
        chars.append('r')
    else:
        chars.append('-')

    if d['group_write']:
        chars.append('w')
    else:
        chars.append('-')

    if d['group_execute']:
        if d['is_setgid']:
            chars.append('s')
        else:
            chars.append('x')
    else:
        if d['is_setgid']:
            chars.append('S')
        else:
            chars.append('-')

    if d['other_read']:
        chars.append('r')
    else:
        chars.append('-')

    if d['other_write']:
        chars.append('w')
    else:
        chars.append('-')

    if d['other_execute']:
        if d['is_sticky']:
            chars.append('t')
        else:
            chars.append('x')
    else:
        if d['is_sticky']:
            chars.append('T')
        else:
            chars.append('-')

    return ''.join(chars)

def str_to_mode(s):
    '''Inverse of mode_to_str().'''
    assert len(s) == 10, 'mode string should be exactly 10 chars: %s' % (s,)

    ret = dict()

    assert s[0] in '-bcdlp'
    ret['is_regular'] = s[0] == '-'
    ret['is_block_device'] = s[0] == 'b'
    ret['is_character_device'] = s[0] == 'c'
    ret['is_directory'] = s[0] == 'd'
    ret['is_symlink'] = s[0] == 'l'
    ret['is_fifo'] = s[0] == 'p'

    assert s[1] in 'r-'
    ret['user_read'] = s[1] == 'r'
    
    assert s[2] in 'w-'
    ret['user_write'] = s[2] == 'w'

    assert s[3] in 'x-sS'
    ret['user_execute'] = (s[3] == 'x') or (s[3] == 's')
    ret['is_setuid'] = (s[3] == 's') or (s[3] == 'S')

    assert s[4] in 'r-'
    ret['group_read'] = s[4] == 'r'
    
    assert s[5] in 'w-'
    ret['group_write'] = s[5] == 'w'

    assert s[6] in 'x-sS'
    ret['group_execute'] = (s[6] == 'x') or (s[6] == 's')
    ret['is_setgid'] = (s[6] == 's') or (s[6] == 'S')

    assert s[7] in 'r-'
    ret['other_read'] = s[7] == 'r'
    
    assert s[8] in 'w-'
    ret['other_write'] = s[8] == 'w'

    assert s[9] in 'x-tT'
    ret['other_execute'] = (s[9] == 'x') or (s[9] == 't')
    ret['is_sticky'] = (s[9] == 't') or (s[9] == 'T')

    return ret

class FileMetaData(object):
    '''Represents meta-data about files, including any and all
    meta-data that are to be preserved on backup/restore.
    
    We make a deliberate effort to provide a high-level abstraction
    rather than POSIX style bit twiddling. We essentially provide a
    dedicated accessor for every relevant piece of information, along
    with methodsfor converting to/from a text format readable both by
    humans (sort of) and ourselves.

    Instances of this class only care about meta data; they know
    nothing of the files to which the meta data appliies, or
    underlying file system operations (construction of FileMetaData
    instances from some actual real file is done by the appropriate
    file system backend).

    Instances of this class are to be treated as read-only, and the
    public interface deliberately makes it difficult to make changes.

    @ivar is_directory        Is the file a directory?
    @ivar is_character_device Is the file a special character device?
    @ivar is_block_device     Is the file a block device?
    @ivar is_regular          Is the file a regularfile?
    @ivar is_fifo             Is the file a FIFO/named pipe?
    @ivar is_symlink          Is the file a symbolic link?
    @ivar is_setuid           Is the setuid bit set?
    @ivar is_setgid           Is the setgid bit set?
    @ivar is_sticky           Is the sticky bit set?
    @ivar user_read
    @ivar user_write
    @ivar user_execute
    @ivar group_read
    @ivar group_write
    @ivar group_execute
    @ivar other_read
    @ivar other_write
    @ivar other_execute

    @ivar uid                 UID of the owner.
    @ivar gid                 GID of the group owner.
    @ivar size                Size of file (if regular, else None).
    @ivar atime               Access time of the file (seconds since epoch).
    @ivar mtime               Modification time of the file (seconds since epoch).
    @ivar ctime               ctime, whatever the platform feels that means (secondssince epoch).
    '''

    # for introspection and automation purposes.
    propnames = [ 'is_directory',
                  'is_character_device',
                  'is_block_device',
                  'is_regular',
                  'is_fifo',
                  'is_symlink',
                  'is_setuid',
                  'is_setgid',
                  'is_sticky',
                  'user_read',
                  'user_write',
                  'user_execute',
                  'group_read',
                  'group_write',
                  'group_execute',
                  'other_read',
                  'other_write',
                  'other_execute',
                  'uid',
                  'gid',
                  'size',
                  'atime',
                  'mtime',
                  'ctime' ]

    def __init__(self, props=None, other=None):
        '''
        @param props: Dict of properties that match those of the instance to be created.
        @param other: Other instance on which to base the values of any properties that
                      do not appear in props.
        '''
        self.__write_protected = False

        if other: # initialize from other instance
            for prop in self.propnames:
                setattr(self, prop, getattr(other, prop))
        else:     # else initialize all to None
            for prop in self.propnames:
                setattr(self, prop, None)

        if props:
            for prop, val in props.iteritems():
                assert prop in self.propnames, 'property %s not a valid property' % (prop,)
                setattr(self, prop, val)

        self.__write_protected = True

    def __setattr__(self, key, value):
        # implement trivial write protection scheme
        if (not key.startswith('_')) and self.__write_protected:
            raise AssertionError('setting a property on FileMetaData is not allowed - we are read-only!')
        else:
            self.__dict__[key] = value

    def __getitem__(self, key):
        if key in self.propnames:
            return getattr(self, key)
        else:
            raise KeyError(key)
        
    @classmethod
    def from_string(cls, s):
        '''Given a string in the format produced by to_string(), parse
        it and return the resulting instance.'''
        comps = s.split()
        
        assert len(comps) == 7, ('expected something with 7 components, like drwxr-xr-x 5 6 7 8 9 10, '
                                 'not like %s' % (s,))

        d = str_to_mode(comps[0]) # grab most flags
        
        d['uid'] = int(comps[1])
        d['gid'] = int(comps[2])
        d['size'] = int(comps[3])
        d['atime'] = int(comps[4])
        d['mtime'] = int(comps[5])
        d['ctime'] = int(comps[6])

        return FileMetaData(d)

    def to_string(self):
        '''Produce a string encoding of this meta data.

        The format of the string is:

          MODESTR uid gid size atime mtime ctime

        Where MODESTR is the result of mode_to_str() (ls -l
        style). Times are seconds since epoch.'''

        assert self.uid is not None
        assert self.gid is not None
        assert self.size is not None
        assert self.atime is not None
        assert self.mtime is not None
        assert self.ctime is not None

        return ('%(modestring)s %(uid)d %(gid)d %(size)d %(atime)d %(mtime)d %(ctime)d'
                '' % dict(modestring=mode_to_str(dict(is_directory=self.is_directory,
                                                      is_character_device=self.is_character_device,
                                                      is_block_device=self.is_block_device,
                                                      is_regular=self.is_regular,
                                                      is_fifo=self.is_fifo,
                                                      is_symlink=self.is_symlink,
                                                      is_setuid=self.is_setuid,
                                                      is_setgid=self.is_setgid,
                                                      is_sticky=self.is_sticky,
                                                      user_read=self.user_read,
                                                      user_write=self.user_write,
                                                      user_execute=self.user_execute,
                                                      group_read=self.group_read,
                                                      group_write=self.group_write,
                                                      group_execute=self.group_execute,
                                                      other_read=self.other_read,
                                                      other_write=self.other_write,
                                                      other_execute=self.other_execute)),
                          uid=self.uid,
                          gid=self.gid,
                          size=self.size,
                          atime=self.atime,
                          mtime=self.mtime,
                          ctime=self.ctime))

