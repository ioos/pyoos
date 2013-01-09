from setuptools import setup, find_packages, Command

files = ["pyoos/*"]
readme = open('README.md', 'rb').read()
reqs = [line.strip() for line in open('requirements.txt')]

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name                = "pyoos",
    version             = "0.2",
    description         = "A Python API into IOOS data",
    long_description    = readme,
    license             = 'LICENSE.txt',
    author              = "Kyle Wilcox",
    author_email        = "kwilcox@sasascience.com",
    url                 = "https://github.com/asascience-open/pyoos",
    packages            = find_packages(),
    cmdclass            = {'test': PyTest},
    install_requires    = reqs,
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
