import sys
from setuptools import setup

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name = 'udif',
    version = '0.0.8',
    description = 'human readable and writable data interchange format',
    long_description = readme,
    long_description_content_type = 'text/x-rst',
    author = "Ken Kundert",
    author_email = 'udif@nurdletech.com',
    download_url = 'https://github.com/kenkundert/udif/tarball/master',
    license = 'GPLv3+',
    zip_safe = False,
    packages = ['udif'],
    install_requires = 'inform>=1.23'.split(),
    python_requires = '>=3.6',
    keywords = 'data'.split(),
    classifiers = [
        'Development Status :: Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
    ],
)
