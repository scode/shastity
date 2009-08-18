# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Individual manifest management.

A manifest contains all information about a particular backup, except
the contents of data blocks. Manifests are assuemd to be of
"managable" size, fitting comfortably in memory.

Manifests in memory are basically lists of (path, metadata, hashes)
tuples. On disk, they are human-readable text as documented in the
manual.

Manifests maintain the order of entries added to it. The preserved
ordering is a public interface, and other modules depend on it (e.g.,
directory creation during materialization, merge comparison for change
time optimization during persistence).

This module deals with creation/storage/retrieval/deletion of
individual backup manifests as well as listing available manifests.

Note that we avoid ever returning a concrete manifest directly, and
expose only very limited functionality. This is for the purpose of
allowing future improvements such as not necessitating that manifests
fit into memory.
'''

from __future__ import absolute_import
from __future__ import with_statement

import  os.path

import shastity.filesystem as filesystem
import shastity.logging as logging

log = logging.get_logger(__name__)

def store_manifest(backend, name, entry_generator):
    """
    @param backend A storage backend (dedicated to manifests)

    @type  name A string.
    @param name Name of manifest.
    
    @param entry_generator Backup entry generator producting all entries, in order, for inclusion
                           in the manifest.
    """
    pass

def read_manifest(backend, name):
    """
    @return A backup entry generator producing all entries, in order,
            contained in the manifest.
    """
    pass

def delete_manifest(backend, name):
    """
    @param backend Storage backend from which to delete the manifest
                   by the given name.

    @param name Name of the manifest to delete.
    """
    pass

def list_manifests(backend):
    """
    @param backend The backend containing the manifests to list.

    @return A list of names of all manifests contained in the backend.
    """
    pass
