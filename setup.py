from __future__ import with_statement
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def extract_version(module='pyoos'):
    version = None
    fdir = os.path.dirname(__file__)
    fnme = os.path.join(fdir, module, '__init__.py')
    with open(fnme) as fd:
        for line in fd:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                # Remove quotation characters.
                version = version.strip()[1:-1]
                break
    return version


def readme():
    with open('README.rst') as f:
        return f.read()

reqs = [line.strip() for line in open('requirements.txt')]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name                = 'pyoos',
    version             = extract_version(),
    description         = 'A Python library for collecting Met/Ocean observations',
    long_description    = readme(),
    license             = 'GPLv3',
    author              = 'Kyle Wilcox',
    author_email        = 'kyle@axiomdatascience.com',
    url                 = 'https://github.com/ioos/pyoos.git',
    packages            = find_packages(),
    install_requires    = reqs,
    tests_require       = ['pytest'],
    cmdclass            = {'test': PyTest},
    classifiers         = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
        ],
    include_package_data = True,
)
