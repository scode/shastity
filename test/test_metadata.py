# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import errno
import os.path
import unittest

import shastity.metadata as metadata

class MetaDataTests(unittest.TestCase):
    def setUp(self):
        pass

    def assertDictEqual(self, d1, d2):
        def diff(s):
            raise AssertionError('dicts not equal; multiple diffs may exist, but '
                                 'first diff found is: %s' % (s,))
        if d1 != d2:
            for key in d1.keys():
                if not key in d2:
                    diff('key %s in d1 but not d2' % (key,))
            for key in d2.keys():
                if not key in d1:
                    diff('key %s in d2 but not d1' % (key,))

            for key in d1.keys():
                if d1.get(key) != d2.get(key):
                    diff('key %s has differing values (%s, %s) in (d1, d2)'
                         '' % (key, d1.get(key), d2.get(key)))
                

    def test_write_protection(self):
        md = metadata.FileMetaData()
        
        def assign_test():
            md.user_write = False
        self.assertRaises(AssertionError, assign_test)

    def test_init_assignment(self):
        for propname in metadata.FileMetaData.propnames:
            for boolval in [ True, False ]:
                propdic = dict()
                propdic[propname] = boolval

                self.assertEqual(getattr(metadata.FileMetaData(props=propdic), propname), boolval)

    def test_other_copy(self):
        for propname in metadata.FileMetaData.propnames:
            for boolval in [ True, False ]:
                propdic = dict()
                propdic[propname] = boolval

                self.assertEqual(getattr(metadata.FileMetaData(other=metadata.FileMetaData(props=propdic)), propname), boolval)

    def test_dict_iface(self):
        for propname in metadata.FileMetaData.propnames:
            for boolval in [ True, False ]:
                propdic = dict()
                propdic[propname] = boolval

                self.assertEqual(metadata.FileMetaData(props=propdic)[propname], boolval)

    def test_mode_strings(self):
        def test_conv(d, s):
            ''' Convert dict to string and make sure it matches
            s. Then convert it back and make sure it results in an
            identical dict.
            '''
            got_s = metadata.mode_to_str(d)
            self.assertEqual(got_s, s)

            got_d = metadata.str_to_mode(got_s)

            self.assertDictEqual(got_d, d)
            
        # common base test
        test_conv(dict(is_directory=True,
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
                       is_sticky=False),
                  'drwxr-xr-x')
        # symlinks are special
        test_conv(dict(is_directory=False,
                       is_regular=False,
                       is_symlink=True,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False),
                  'lrwxr-xr-x')

        # misc permutations, one character at a time
        test_conv(dict(is_directory=False,
                       is_regular=True,
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
                       is_sticky=False),
                  '-rwxr-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=False,
                       is_symlink=False,
                       is_block_device=True,
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
                       is_sticky=False),
                  'brwxr-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=False,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=True,
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
                       is_sticky=False),
                  'crwxr-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
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
                       is_sticky=False),
                  '--wxr-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=True,
                       group_read=True,
                       group_write=False,
                       group_execute=True,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
        '---xr-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=True,
                       group_write=False,
                       group_execute=True,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
                  '----r-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=True,
                       group_write=False,
                       group_execute=True,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=True,
                       is_setgid=False,
                       is_sticky=False),
                  '---Sr-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=True,
                       group_read=True,
                       group_write=False,
                       group_execute=True,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=True,
                       is_setgid=False,
                       is_sticky=False),
                  '---sr-xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=True,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
                  '------xr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=True,
                       group_execute=True,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
                  '-----wxr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=False,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
                  '-------r-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=False,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=True,
                       is_sticky=False),
        '------Sr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=True,
                       other_read=True,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=True,
                       is_sticky=False),
                  '------sr-x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=False,
                       other_read=False,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
                  '---------x')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=False,
                       other_read=False,
                       other_write=True,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
                  '--------wx')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=False,
                       other_read=False,
                       other_write=False,
                       other_execute=False,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=False),
                  '----------')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=False,
                       other_read=False,
                       other_write=False,
                       other_execute=False,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=True),
                  '---------T')
        test_conv(dict(is_directory=False,
                       is_regular=True,
                       is_symlink=False,
                       is_block_device=False,
                       is_character_device=False,
                       is_fifo=False,
                       user_read=False,
                       user_write=False,
                       user_execute=False,
                       group_read=False,
                       group_write=False,
                       group_execute=False,
                       other_read=False,
                       other_write=False,
                       other_execute=True,
                       is_setuid=False,
                       is_setgid=False,
                       is_sticky=True),
                  '---------t')

    def test_to_string(self):
        d = dict(is_directory=True,
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
                 uid=5,
                 gid=6,
                 size=7,
                 atime=8,
                 mtime=9,
                 ctime=10)
        md = metadata.FileMetaData(d)

        self.assertEqual(md.to_string(), 'drwxr-xr-x 5 6 7 8 9 10')

if __name__ == "__main__":
    unittest.main()
