# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
Configuration handlng.

Provides some infra-structure for expressing and dealing with the
configuration of shastity, hopefully in a way which caters both to
creating a user-friendly command line interface and a user-friendly
library API for Python callers.
"""

from __future__ import absolute_import
from __future__ import with_statement

class RequiredOptionMissingError(Exception):
    """
    Raised to indicate an option value was mssing, where it was in
    fact required.

    @ivar option_name The name of the option whose value is missing.
    @ivar comment A human-readable comment providing further details, or
                  None if not available.
                  """
    def __init__(self, option_name, comment=None):
        """
        @param option_name The value to assign to self.option_name
        @param comment The value to assign to self.comment
        """
        self.option_name = option_name
        self.comment = comment

class Option:
    """
    Abastract base class defining the interface for all options. An
    option is some configuration "knob" that has a name and a value
    that has to satisfy certain criteria. An interface is provided for
    handling options in a generic fashion.

    Methods beginning with an underscore are intended for
    implementation by subclasses.
    """
    def parse(self, s):
        """
        Parse a string representation of the desired value of the
        option.

        @raise Exceptoin If the string cannot be parsed.
        @raise Exception If the resulting value after parsing is invald.
        """
        pass

    def set(self, value):
        """
        Set the value of the option.

        @raise An exception if the value is nod valid for this option.
        """
        pass

    def get(self):
        """
        Return the current value of this option, or None if there is
        none (not distingushed from an actual option value of None).

        @returns The value.
        """
        pass

    def get_required(self):
        """
        Return the current value of this option, or raise an exception
        if one is not available. This is intended to be used when
        asking for options where the code requires that it be
        available, in a way which should generate an error containing
        reasonably user-friendly error information.

        @raise RequiredOptionMissingError

        @return The current value.
        """
        pass
