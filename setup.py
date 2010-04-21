#!/usr/bin/env python

from distutils.core import setup

from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
setup(name = 'grounding',
        version = '0.0',
        description = 'Learning to ground sensory data using OMCS',
        author = 'Catherine Havasi and Rob Speer',
        author_email = 'conceptnet@media.mit.edu',
        packages = ['grounding'],
        package_dir = {'grounding': 'grounding'},
        package_data = {'grounding': ['nodebox_data/*.txt']},
        #scripts = ['path/to/script']
        )
