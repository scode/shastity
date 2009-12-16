# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Misc utilities.
'''

def bind(callable, *bind_args, **bind_kwargs):
    """
    Create a callable which, when called, will call the given callable
    with its bound arguments and the arguments actually given in the
    call.

    The primary use case is to capture variables for use when creating
    lambdas for deferred and/or asynchronous execution. For example,
    consider::

      for x, y in something():
        schedule(lambda arg: do_something(x, y, arg))

    Assume the callable given to schedule() will be called with one
    argument (arg).

    Assuming schedule() won't call the lambda until at a future time,
    this code is subtly broken because the closure the lambda function
    closes over the x and y *bindings* rather than the values they
    have at the time of the lambda creation.

    Using this function, the example above would instead be written
    as:

      for x, y in something():
        schedule(bind(lambda x,y, arg: do_something(x, y), x, y))

    Suggestions for how to do this less verbosely and more cleanly are
    welcome.
    """
    def caller(*args, **kwargs):
        actual_args = bind_args + args

        actual_kwargs = bind_kwargs
        actual_kwargs.update(kwargs)

        return callable(*actual_args, **actual_kwargs)

    return caller
