# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''

Very simple string encoding/decoded specifically for the purpose of
including characterstrings (NOT byte strings!) into whitespace
separated content.

Please see doc/string_handling.txt for some thoughts on character
strings vs. byte strings.

The encoding is simply as follows:

At the character string level:

  - All strings are encoded in UTF-8.

At the resulting byte string level:

  - All strings are enclosed in single-quotes (in order to be able to represent
    the empty string).
  - All whitespace and single-quotes are encoded in URL encoding style (%xx).
  - The character '%' itself is encoded.
  - Various additional byte values are encoded using %xx style even if they are
    7 bit, with the intended result of avoiding characters that tend to interacti
    with shells, be problematic to display or cut'n'paste etc.

Decoding is simply a matter of:

  - Remove enclosing ''
  - URL-decode the remaining byte string.
  - Decode the resulting byte string as UTF-8.

Note that we convert from character strings to US ASCII character
strings; any converion to byte strings are beyond the scope of this
module.
'''

# Manually maintained string of character that we don't escape, mostly
# for readability (and brevity/size).
_safechars = 'abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789_-:.'

# Define two utilities that we only use on import to generate _enc_map.
def _hex(c):
    return '%%%02X' % (ord(c),)

def _hex_if_needed(c):
    if c not in _safechars:
        return _hex(c)
    else:
        return c

# And the _enc_map, which simply maps characters to their encoded-if-needed version.
_enc_map = dict([ (chr(c), _hex_if_needed(chr(c))) for c in xrange(0, 256) ])

# And these two guys are used by the public interface.
def _urlenc(s):
    return ''.join([ _enc_map[c] for c in s ])

def _urldec(s):
    parts = s.split('%')

    # for each part but the first, decode based on the first two
    # characters and replace destructively
    for i in xrange(1, len(parts)):
        assert len(parts[i]) >= 2, 'broken string, expected hex after %%: %s' % (s,)
        unhexed = chr(int(parts[i][0] + parts[i][1], 16))
        parts[i] = unhexed + parts[i][2:]

    return ''.join(parts)

def spencode(s):
    '''
    @param s: Character string to encode.
    
    @return A ASCII character string as per the description in the
            module documentation.
    '''
    bytestr = s.encode('utf-8')

    asciistr = "'%s'" % (_urlenc(bytestr))

    return asciistr

def spdecode(s):
    '''
    @param s: ASCII character string to decode.

    @return The decoded character string.
    '''
    assert len(s) >= 2
    assert s[0] == "'"
    assert s[len(s) - 1] == "'"
    
    bytestr = _urldec(s[1:len(s) - 1])

    return bytestr.decode('utf-8')
