#!/usr/bin/env python

from distutils.core import setup
import setuptools


setup(
    name='dndme',
    version='0.0.2',
    description='Tools for helping the DM run Dungeons & Dragons sessions.',
    author='Mike Pirnat',
    packages=setuptools.find_packages(),
    install_requires=[
        'attrs',
        'click',
        'prompt-toolkit',
        'pytoml',
        'six',
        'wcwidth',
    ],
    extras_require={
        'test': [
            'coverage',
            'pytest',
            'pytest-cov',
            'pytest-runner',
            'tox',
            'pylint',
        ],
        'dev': [
            'pip-tools',
        ],
    },
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    entry_points={
        'console_scripts': [
            'dndme = dndme.shell:main_loop',
        ],
    }
)
