# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

_map = dict(debug=8,
            info=5,
            notice=4,
            warning=3,
            error=2,
            critical=1)

class InvalidVerbosityLevel(Exception):
    pass

def to_level(verbosity):
    """
    Given a verbosity (int), return its closest log level. If an exact
    match does not exist, return one that that will include a subset
    of the requested amount of information.
    """
    candidates = [ v for k, v in _map.iteritems() if v <= verbosity ]

    if not candidates:
        raise InvalidVerbosityLevel(verbosity)

    return reduce(max, candidates)
