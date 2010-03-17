# -*- coding: utf-8 -*-

# Copyright (c) 2010 Thomas Habets <thomas@habets.pp.se>

from __future__ import absolute_import
from __future__ import with_statement

import subprocess
import os
import struct
import re
from Crypto.Cipher import AES

import shastity.backend as backend
import shastity.hash as hash

class AutoClose(object):
    def __init__(self, fd):
        self.fd = fd
    def __del__(self):
	if not self.fd is None:
            os.close(self.fd)
    def fdopen(self, rw):
        ret = os.fdopen(self.fd, rw)
        self.fd = None
        return ret
    def fileno(self):
        return self.fd

def pipeWrap():
    return [AutoClose(x) for x in os.pipe()]

def enc(key, data):
    return encDec(key,data,extra='-c --force-mdc')

def dec(key, data):
    return encDec(key,data,extra='')

def encDec(key, data, extra):
    def doClose(*fds):
        """doClose()
        Write end of password pipe must be closed in child process.
        """
        [os.close(x.fd) for x in fds]

    # password pipe
    pass_r, pass_w = pipeWrap()
    p = subprocess.Popen(("/usr/bin/gpg -q --batch %s "
                          + " --compress-level 0 --passphrase-fd %d")
                         % (extra, pass_r.fileno()),
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=None,
                         preexec_fn=lambda: doClose(pass_w),
                         shell=True)
    del pass_r

    # write password & close
    with pass_w.fdopen('w') as f:
        f.write(key)

    # write data
    p.stdin.write(data)
    p.stdin.close()

    # subprocess expects p.stdin to be open, so endulge it
    p.stdin = open('/dev/null','w')

    # Get results
    ret = p.stdout.read()
    if p.wait():
        raise "GPG failed"
    return ret

class BackendWrapper(backend.Backend):
    def __init__(self, next):
        self.next = next

    def put(self, *args):
        return self.next.put(*args)

    def get(self, *args):
        return self.next.put(*args)

    def list(self, *args):
        return self.next.list(*args)
    
class DataCryptoGPG(BackendWrapper):
    def __init__(self, next, cryptoKey):
        BackendWrapper.__init__(self, next)
        self.cryptoKey = cryptoKey

    def put(self, key, data):
        return self.next.put(key, enc(self.cryptoKey, data))

    def get(self, key):
        return dec(self.cryptoKey, self.next.get(key))

class NameCrypto(BackendWrapper):
    def __init__(self, next, cryptoKey):
        BackendWrapper.__init__(self, next)
        self.cryptoKey = hash.make_hasher('sha512')(cryptoKey)[1]

    def put(self, key, data):
        return self.next.put(self.__enc(key), data)

    def get(self, key):
        return self.next.get(self.__enc(key))

    def list(self):
        return [self.__dec(x) for x in self.next.list()]

    def __enc(self, name):
        crypt = AES.new(self.cryptoKey[:16], AES.MODE_CBC)
        s = struct.pack("!l", len(name)) + name
        if len(s) % 16:
            s = s + " " * (16 - len(s) % 16)
        ret = crypt.encrypt(s)
        return ''.join(["%.2x" % (ord(x)) for x in ret])

    def __dec(self, cfn):
        crypt = AES.new(self.cryptoKey[:16], AES.MODE_CBC)
        s = ''.join([chr(int(x,16)) for x in re.findall('(..)', cfn)])
        dec = crypt.decrypt(s)
        l = struct.unpack("!l", dec[:4])[0]
        return dec[4:4+l]
