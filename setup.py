#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open('Version', 'rb') as f:
    version = next(f).strip().decode('utf-8')

with open('README.rst') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = [r for r in f]

__doc__ = readme

setup(
    name='redis_pubsub_dict',
    version=version,
    url='https://github.com/Richard-Mathie/py-redis-pubsub-dict',
    license='GNU GPLv2',
    author='Richard Mathie',
    author_email='richard.mathie@cantab.net',
    description='A python class for using redis, or other key value stores, and caching the values for read heavy workloads',
    long_description=__doc__,
    py_modules=['redis_pubsub_dict'],
    platforms='any',
    install_requires=requirements,
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)
