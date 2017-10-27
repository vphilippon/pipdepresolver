#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup               


setup(                                                    
    name='pipdepresolver',
    use_scm_version=True,
    description="A simplistic pip-based Python dependency resolver.",
    author='Vincent Philippon',
    author_email='vince.philippon+pipdepresolver@gmail.com',
    url='https://github.com/vphilippon/pipdepresolver/',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    setup_requires=['setuptools_scm'],
    install_requires=[
        'click>=6',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pipdepresolver = pipdepresolver.cli:cli',
        ],
    },
    platforms='any',
    classifiers=[
        # TODO
    ]
)