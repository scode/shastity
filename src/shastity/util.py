# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Misc utilities.
'''

def bind(callable, *bind_args, **bind_kwargs):
    def caller(*args, **kwargs):
        actual_args = bind_args + args

        actual_kwargs = bind_kwargs
        actual_kwargs.update(kwargs)

        return callable(*actual_args, **actual_kwargs)

    return caller
