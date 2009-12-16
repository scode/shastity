#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name="shastity",
      version="0.0",
      author="Peter Schuller",
      author_email="peter.schuller@infidyne.com",
      packages = ['shastity',
                  'shastity.backends'],
      package_dir = {'': 'src'},
      scripts = ['bin/shastity'])


