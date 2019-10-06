#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'numpy',
    'matplotlib',
    'sortedcontainers',
    'cffi',
    'cairocffi'
]

test_requirements = [
    'pylint'
]

setup(
    name='persispy',
    version='0.0.1',
    description="A python package for persistent homology.",
    long_description=readme + '\n\n' + history,
    packages=['persispy'],
    author="Benjamin Antieau",
    author_email='benjamin.antieau@gmail.com',
    url='https://github.com/benjaminantieau/persispy',
    platforms='any',
    cmdclass={'build_ext':build_ext},
    setup_requires=["numpy"],  # numpy install requires this
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='persispy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU GPL v2',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
