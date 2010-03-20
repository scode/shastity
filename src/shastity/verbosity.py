# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

import shastity.logging as logging

_name_map = dict(DEBUG=8,
                 INFO=5,
                 NOTICE=4,
                 WARNING=3,
                 ERROR=2,
                 CRITICAL=1)

_level_map = dict([(getattr(logging, k), k) for k, v in _name_map.iteritems() ])

class InvalidVerbosityLevel(Exception):
    pass

def to_level(verbosity):
    """
    Given a verbosity (int), return its closest log level. If an exact
    match does not exist, return one that that will include a subset
    of the requested amount of information.
    """
    candidates = [ (k, v) for k, v in _name_map.iteritems() if v <= verbosity ]

    if not candidates:
        raise InvalidVerbosityLevel(verbosity)

    def better_candidate(a, b):
        if a[1] > b[1]:
            return a
        else:
            return b

    best_name, best_level = reduce(better_candidate, candidates)

    return getattr(logging, best_name)

def to_verbosity(level):
    """
    Given a log level (level from the logging module), return its
    verbosity level.
    """
    if not level in _level_map:
        raise InvalidLogLevel(level)

    return _name_map[_level_map[level]]
