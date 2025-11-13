#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup


def get_long_description():
    with open('README.md', encoding='utf8') as f:
        return f.read()


def get_packages(package):
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


setup(
    name='adc-aios3',
    version='0.1.0',
    url='https://github.com/ascet-dev/adc-aios3',
    python_requires='>=3.8',
    install_requires=[
        'aiobotocore>=2.5.0',
        'botocore>=1.29.0',
    ],
    license='MIT',
    description='Async S3 client with lifecycle management',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    packages=get_packages('adc_aios3'),
    include_package_data=True,
    data_files=[('', [])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    zip_safe=False,
)
