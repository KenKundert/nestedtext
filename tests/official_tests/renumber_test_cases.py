#!/usr/bin/env python3

"""
Renumber the test cases such that the numbers within each family count 
consecutively from 1.

Usage:
    renumber_test_cases.py [<cases>]...

Arguments:
    <cases>
        The test cases to renumber.  By default, all cases will be renumbered.

The numbers in the test names don't have any real significance, but sometimes 
it's just nice to keep related tests close together in number.  For example, 
imagine we want to add two new test cases that are similar to the existing case 
"dict_4".  We could name these tests "dict_4a" and "dict_5b", then use this 
script to renumber them to "dict_5" and "dict_6" without overwriting any 
existing tests.
"""

import docopt
import shutil
from tempfile import mkdtemp
from pathlib import Path
from more_itertools import bucket

ROOT_DIR = Path(__file__).parent
CASE_DIR = ROOT_DIR / 'test_cases'

import sys; sys.path.append(str(ROOT_DIR / 'api'))
import nestedtext_official_tests as official

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    tmp_dir = Path(mkdtemp(prefix='renumber_test_cases_'))
    cases = official.load_test_cases(args['<cases>'])

    families = bucket(cases, key=lambda x: x.family)
    for key in families:
        sorted_cases = sorted(families[key], key=lambda x: x.num)
        d = len(str(len(sorted_cases)))
        for i, case in enumerate(sorted_cases, 1):
            shutil.move(case.dir, tmp_dir / f'{case.family}_{i:0{d}}')

    for dir in tmp_dir.iterdir():
        shutil.move(dir, CASE_DIR / dir.name)

    tmp_dir.rmdir()
