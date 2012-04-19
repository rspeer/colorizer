#!/usr/bin/env python

from setuptools import setup

from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
setup(name = 'colorizer',
        version = '0.1',
        description = 'Associating text with colors using ConceptNet',
        author = 'Catherine Havasi and Rob Speer',
        author_email = 'conceptnet@media.mit.edu',
        packages = ['colorizer'],
        package_dir = {'colorizer': 'colorizer'},
        package_data = {'colorizer': ['data/nodebox/*.txt', 'data/x11/*.txt']},
        #scripts = ['path/to/script']
        )
