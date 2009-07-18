# -*- coding: utf-8 -*-

"""
Provides a simple hashing interface. A "hashers" is a callable, taking
a bytestring, which returns a tuple (hash_algo_name,
hexdigest). make_hasher() is used to construct such a hasher, taking
the name of a supported hashing algorithm.

Example use::

  hasher = make_hasher('sha512')
  hasher('byte string to be hashed')
"""

from __future__ import absolute_import
from __future__ import with_statement

import hashlib

def UnsupportedHashAlgorithm(Exception):
    pass

_all_supported_hashlib_algos = [ 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'md5' ]
_our_supported_hashlib_algos = [ 'sha512' ]

def make_hasher(name):
    """
    @name name: Name of hashes (e.g., 'sha512').
    @return a hasher (= callable, byte string -> (hash_name, hash)).
    """
    if name in _our_supported_hashlib_algos:
        return _hashlib_hasher(name)
    else:
        raise UnsupportedHashAlgorithm(name)

def _hashlib_hasher(name):
    def hasher(bstring):
        h = getattr(hashlib, name)()
        h.update(bstring)
        return (name, h.hexdigest())
    return hasher

