#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages, Extension

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Meinolf Sellmann",
    author_email='info@insideopt.com',
    python_requires='>=3.8.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows'
    ],
    description="InsideOpt Seeker Distribution for Windows, Linux, and Mac",
    install_requires=requirements,
    long_description=readme, 
    keywords='insideopt, seeker, optimization',
    name='ioseeker',
    test_suite='tests',
    version='0.2.4',
    packages=find_packages(include=['seeker', 'seeker.*', '*.so', '*.pyd', '*.dll']),
    package_data={'seeker': ['*.so', 'seeker.py', 'bin/*', 'scripts/*', '*.pyd', '*.dll']},
    zip_safe=False,
)
