# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import shastity.backend as backend
import shastity.logging as logging

log = logging.get_logger(__name__)

def delayed_imports():
    global connection
    import boto.s3.connection as connection

    global key
    import boto.s3.key as key

class S3Backend(backend.Backend):
    ''' 
    Amazon S3 backend.

    Currently this requires the AWS_ACCESS_KEY_ID and
    AWS_SECRET_ACCESS_KEY environment variables to be set (picked up
    directly by the boto library). This should be documented in better
    detail in the future, and we should be able to take this
    information as configuration options instead of from the
    environment.

    For information on Amazon S3, see:

        http://aws.amazon.com/s3/
    '''
    def __init__(self, identifier, opts=dict()):
        backend.Backend.__init__(self, identifier, opts)

        delayed_imports()

        self.bucket_name = identifier
        self.__opts = opts

        self.__connect()

    def __connect(self):
        '''Connect, leaving self.__conn and self.__bucket valid.'''
        self.__conn = None   # make sure it's bound even on failure
        self.__bucket = None # ditto

        log.debug('attempting to connect to s3')
        self.__conn = connection.S3Connection(host=self.__opts.get('s3_host', connection.S3Connection.DefaultHost))
        self.__conn.calling_format = connection.SubdomainCallingFormat()
        self.__bucket = self.__conn.lookup(self.bucket_name)

    def exists(self):
        if self.__bucket is not None:
            self.__bucket = self.__conn.lookup(self.bucket_name)

        return self.__bucket is not None

    def create(self):
        if not self.exists():
            # automatically create if it does not exist
            log.log(logging.NOTICE,
                    's3 bucket %s does not exist; attempting to create',
                    self.bucket_name)

            # TODO: should bail if location is not configured (and
            # even if we were to default default to US instead of
            # EU; defaulting to EU temporarily during development
            # for egotistical practical purposes)
            location = self.__opts.get('bucket_location', 'EU')
            if location == 'EU':
                location = connection.Location.EU
            elif location == 'DEFAULT':
                location = connection.Location.DEFAULT
            else:
                raise AssertionError('invalid bucket location: %s' % (location,))

            self.__bucket = self.__conn.create_bucket(self.bucket_name,
                                                      location=location)
            raise self.__bucket, 'bucket creation failed, though no exception was raised'
        
    def put(self, name, data):
        k = key.Key(bucket=self.__bucket,
                    name=name)

        k.set_contents_from_string(data,
                                   headers={'Content-Type': 'application/octet-stream'})
            
    def get(self, name):
        k = key.Key(bucket=self.__bucket,
                    name=name)

        return k.get_contents_as_string()

    def list(self):
        return [ k.name for k in self.__bucket.list() ]

    def delete(self, name):
        self.__bucket.delete_key(name)

    def close(self):
        pass # boto doesn't need explicit disconnect
        
