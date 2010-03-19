# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Individual manifest management.

A manifest contains all information about a particular backup, except
the contents of data blocks. Manifests are assumed to be of
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
import re

import shastity.filesystem as filesystem
import shastity.logging as logging
import shastity.metadata as metadata
import shastity.spencode as spencode

log = logging.get_logger(__name__)

class ManifestError(Exception):
    def __init__(self, lineno, line, msg):
        self.lineno = lineno
        self.line = line
        self.msg = msg

def write_manifest(backend, name, entry_generator):
    """
    @param backend A storage backend (dedicated to manifests)

    @type  name A string.
    @param name Name of manifest; must not contain dots.
    
    @param entry_generator Backup entry generator producting all
                           entries, in order, for inclusion in the
                           manifest.
    """
    assert '.' not in name, 'manifest names cannot contain dots'

    mf_lines = ['shastity',
                'version 1',
                'end']

    for (path, metadata, hashes) in entry_generator:
        md = metadata.to_string()

        pth = spencode.spencode(path)

        rest = ' '.join([ '%s,%s' % (algo, hex) for (algo, hex) in hashes ])

        mf_lines.append('%s | %s | %s' % (md, pth, rest))

    backend.put(name, '\n'.join(mf_lines))

def read_manifest(backend, name):
    """
    @return A backup entry generator producing all entries, in order,
            contained in the manifest.
    """
    assert '.' not in name, 'manifest names cannot contain dots'
    
    mf_lines = [ line.strip() for line in backend.get(name).split('\n') ]

    version = None
    lineno = 1

    if len(mf_lines) == 0:
        raise ManifestError(lineno,
                            '',
                            "Manifest empty")

    if  mf_lines[0] != 'shastity':
        raise ManifestError(lineno,
                            mf_lines[0],
                            "First line not 'shastity'")

    lineno += 1

    for head in mf_lines[lineno-1:]:
        lineno += 1

        if head == 'end':
            break

        # version
        m = re.match(r'version (\d+)', head)
        if m:
            version = int(m.group(1))

        # unknown
        else:
            raise ManifestError(lineno,
                                head,
                                "Invalid header line: %s" % (head))

    if len(mf_lines) == 0:
        raise ManifestError(lineno,
                            '',
                            "Header error or no data.")

    if version is None:
        raise ManifestError(lineno,
                            '',
                            "Required manifest header 'version' missing")

    for line in mf_lines[lineno-1:]:
        lineno += 1
        (md, path, rest) = [ s.strip() for s in line.split('|') ]

        md = metadata.FileMetaData.from_string(md)
        path = spencode.spdecode(path)
        
        if rest:
            rest = [ (algo, hex) for (algo, hex) in [ pair.split(',') for pair in rest.split() ] ]
        else:
            rest = []

        yield (path, md, rest)

def delete_manifest(backend, name):
    """
    @param backend Storage backend from which to delete the manifest
                   by the given name.

    @param name Name of the manifest to delete.
    """
    backend.delete(name)

def list_manifests(backend):
    """
    @param backend The backend containing the manifests to list.

    @return A list of names of all manifests contained in the backend.
    """
    return backend.list()
