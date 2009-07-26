# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

'''
Storage queue - provides an asynchronous interface for executing
storage operations.

This is the part of shastity which drives concurrency with respect to
backend operations. The public interface of a StorageQueue is
asynchronous except to the extent that it provides blocking waits for
rate limiting purposes.

The intent is that the front-end can schedule storage operations as
fast as the storage queue will allow, allowing the latter to execute
operations independently and concurrently using multiple instantiated
backends.

The front-end is responsible for ensuring that operations that depend
on each other are performed in the correct order, by appropriate use
of the StorageQueue interface.

The storage queue is also the place where retry logic is implemented
(which is easy, given that all backend operations are idempotent).
'''

from __future__ import absolute_import
from __future__ import with_statement

import thread
import threading

import shastity.logging as logging
import shastity.util as util

log = logging.get_logger(__name__)

class StorageOperation(object):
    '''Abstract base class for all operations.

    Specific baseclasses should implement execute().'''
    
    def __init__(self, mnemonic, description, callback=None):
        '''
        @param mnemonic Short mnemonic indicating the type of operation.
        @param description Longer human-readable description of operations.
        @param callback If given, a callable which will be called with the result
                        if and when if the operation is successful.
        '''
        self.mnemonic = mnemonic
        self.description = description
        self.callback = callback

        self.__sq = None
        self.__result = None
        self.__lock = threading.Lock() # protects __result only

    def is_done(self):
        '''Is the operation done? Always safe to call.'''
        with self.__lock:
            return self.__result is not None

    def succeeded(self):
        '''Did it succeed? Calls to this method are invalid before an
        operation is in fact done. However calling code can assume
        that it is done after having wait():ed on the queue to which
        it was submitted, and need not check is_done() on individual
        operations.'''
        with self.__lock:
            assert self.__result is not None, 'succeeeded() called before operation was done'
            return self.__result[0]

    def value(self):
        '''Value of operation, if it succeeded.'''
        with self.__lock:
            assert self.__result is not None, 'value() called before operation was done'
            assert self.__result[0], 'value() called on failed operation'
            return self.__result[1]

    def __set_result(self, success, data):
        with self.__lock:
            assert self.__result is None, '__set_result called twice?'
            self.__result = (success, data)

    def execute(self, backend):
        raise NotImplementedError

    def set_storage_queue(self, sq):
        '''Associate this operation with the given queue, meaning that
        the operation will notify the queue when done. Must only be
        called once.'''
        assert self.__sq is None, 'duplicate call to set_storage_queue()'

        self.__sq = sq

    def perform(self, backend):
        '''Perform the operation (call execute()) using the
        appropriate scaffolding to handling errors and result
        signalling. This will be called by the StorageQueue in some
        worker thread. Errors should not leak from this method (they
        are not well handled).'''
        try:
            log.info('performing operation: %s', str(self))
            self.__set_result(True, self.execute(backend))
            log.debug('operation done: %s', str(self))

            self.__sq.notify_operation_complete(self)
        except Exception, e:
            self.__set_result(False, util.current_traceback())

            log.error('operation failed: %s', str(self))
            log.error('traceback: %s', self.__result[1])

            self.__sq.notify_operation_failed(self)

        if self.__result[0] and self.callback:
            self.callback(self.__result[1])

    def __str__(self):
        return '%s %s' % (self.mnemonic, self.description)

    def __repr__(self):
        return '<%s(%s %s)>' % (self.__class__.__name__, self.mnemonic, self.description)

class PutOperation(StorageOperation):
    def __init__(self, name, data, callback=None):
        StorageOperation.__init__(self, 'PUT', '%s (%d bytes)' % (name, len(data)), callback)

        self.name = name
        self.data = data

    def execute(self, backend):
        return backend.put(self.name, self.data)

class GetOperation(StorageOperation):
    def __init__(self, name, callback=None):
        StorageOperation.__init__(self, 'GET', name, callback)

        self.name = name

    def execute(self, backend):
        return backend.get(self.name)

class DeleteOperation(StorageOperation):
    def __init__(self, name, callback=None):
        StorageOperation.__init__(self, 'DEL', name, callback)

        self.name = name

    def execute(self, backend):
        return backend.delete(self.name)

class OperationHasFailed(Exception):
    pass

class StorageQueue(object):
    def __init__(self, backend_factory, max_conc):
        '''
        @param backend_factory: Callable which will yield a newly constructed backend when called.
        @param max_conc: Maximum worker concurrency.
        '''
        self.backend_factory = backend_factory
        self.max_conc = max_conc
        
        # We maintain a set of currently oustanding operations. We
        # never keep more here than the number of workers that we
        # have; so in effect the current implementation is not really
        # a queue, but rather a manager of a number of slots. A future
        # improvement is to actually support a small queue in order to
        # allow optimal use of available workers (without it workers
        # will be idle as the front-end struggles to generate more
        # work for us when we have a slot free).
        #
        # The associated condition is signalled whenever an item is
        # removed from the dict. Its lock also protects access to the
        # backend cache.
        #
        # For the moment, we keep it simple.
        self.__ops = set()
        self.__backends = set() # backend cache
        self.__cond = threading.Condition()

        self.__failed = False # set to true when an operation fails

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass #self.wait()

    def enqueue(self, op):
        '''Enqueue an operation for execution as soon as possible.
        
        @param op: A StorageOperation instance.'''
        if self.__failed:
            raise OperationHasFailed('a previous operation has failed; refusing further work')

        with self.__cond:
            while len(self.__ops) >= self.max_conc:
                self.__cond.wait()
            self.__ops.add(op)
            self.__start_op(op)

    def __start_op(self, op):
        '''@pre self.__cond locked'''
        # We should maintain a thread pool, but for simplicity in the
        # initial implementation we just launch a dedicated thread.
        if self.__backends:
            backend = self.__backends.pop()
        else:
            log.debug('instantiating new backend')
            backend = self.backend_factory()

        def op_runner():
            op.set_storage_queue(self)
            op.perform(backend)

        thread.start_new_thread(op_runner, ())

    def __remove_op(self, op, success):
        with self.__cond:
            assert op in self.__ops, 'got notify from unknown operation %s' % (str(op,))
            
            if not success:
                self.__failed = True

            self.__ops.remove(op)
            self.__cond.notify()

    def notify_operation_complete(self, op):
        self.__remove_op(op, True)

    def notify_operation_failed(self, op):
        self.__remove_op(op, False)

    def barrier(self):
        '''Guarantee that all operations queued before this call
        execute prior to any operations queued after this call.

        @note The current implementation simply blocks, but that may
              change in the future. If you *want* blocking, sue
              wait().'''
        self.wait()

    def wait(self):
        '''Wait for all outstanding operations to complete.'''
        with self.__cond:
            while self.__ops:
                self.__cond.wait()

        if self.__failed:
            raise OperationHasFailed('one or more operations failed')
