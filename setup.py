#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'psutil',
    'bottle',
    'pyyaml',
    'docopt',
    'bottle',
    'gevent',
    'python-socketio',
    'jinja2',
]

setup_requirements = [
    # TODO(benthomasson): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='performance_pipeline',
    version='0.1.0',
    description="A pipeline to measuring software performance",
    long_description=readme + '\n\n' + history,
    author="Ben Thomasson",
    author_email='bthomass@redhat.com',
    url='https://github.com/benthomasson/performance_pipeline',
    packages=find_packages(include=['performance_pipeline']),
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='performance_pipeline',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
