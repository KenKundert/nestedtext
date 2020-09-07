from setuptools import setup

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name = 'nestedtext',
    version = '0.4.0',
    description = 'human readable and writable data interchange format',
    long_description = readme,
    long_description_content_type = 'text/x-rst',
    author = "Ken Kundert",
    author_email = 'nestedtext@nurdletech.com',
    url = 'https://nestedtext.readthedocs.io',
    download_url = 'https://github.com/kenkundert/nestedtext/tarball/master',
    license = 'GPLv3+',
    zip_safe = False,
    py_modules = 'nestedtext'.split(),
    install_requires = 'inform>=1.23'.split(),
    python_requires = '>=3.6',
    keywords = 'data'.split(),
    classifiers = [
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities',
    ],
)
