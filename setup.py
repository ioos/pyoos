from __future__ import (
    absolute_import,
    division,
    print_function,
    with_statement,
)

from setuptools import find_packages, setup

import versioneer


def readme():
    with open("README.rst") as f:
        return f.read()


reqs = [line.strip() for line in open("requirements.txt")]


setup(
    name="pyoos",
    version=versioneer.get_version(),
    description="A Python library for collecting Met/Ocean observations",
    long_description=readme(),
    license="GPLv3",
    author="Kyle Wilcox",
    author_email="kyle@axiomdatascience.com",
    url="https://github.com/ioos/pyoos.git",
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=reqs,
    tests_require=["pytest"],
    cmdclass=versioneer.get_cmdclass(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
    ],
    include_package_data=True,
)
