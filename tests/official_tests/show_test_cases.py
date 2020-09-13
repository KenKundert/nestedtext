#!/usr/bin/env python3

"""\
Quickly show test inputs and outputs.

Usage:
    show_test_cases.py [<cases>]... [options]

Arguments:
    <cases>
        The test cases to show.  By default, all cases will be shown.

Options:
    -l --load
        Only show test cases for the load() function.

    -d --dump
        Only show test cases for the dump() function.

    -s --success
        Only show test cases that are meant to be successfully loaded/dumped.

    -e --error
        Only show test cases that are meant to trigger errors

    -o --output
        Show the expected output for each case.  The expected inputs, 
        respectively, are always shown.
"""

import docopt
from pathlib import Path
from textwrap import indent

ROOT_DIR = Path(__file__).parent

import sys; sys.path.append(str(ROOT_DIR / 'api'))
import nestedtext_official_tests as official

def show_file(input_output, load_dump, is_success, path):
    success_error = "success" if is_success else "error"
    print(f"  {load_dump.title()} {success_error} ({input_output}):")
    print(indent(path.read_text(), '   │'))

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    cases = official.load_test_cases(args['<cases>'])

    for case in cases:
        if args['--success'] and not case.is_success_case(): continue
        if args['--error'] and not case.is_error_case(): continue

        print(case.dir)

        if not args['--dump'] and case.is_load_case():
            show_file(
                    'input', 'load',
                    case.is_load_success(),
                    case['load']['in']['path'],
            )
            if args['--output']:
                key = 'out' if case.is_load_success() else 'err'
                show_file(
                        'output', 'load',
                        case.is_load_success(),
                        case['load'][key]['path'],
                )

        if not args['--load'] and case.is_dump_case():
            show_file(
                    'input', 'dump',
                    case.is_dump_success(),
                    case['dump']['in']['path'],
            )
            if args['--output']:
                key = 'out' if case.is_dump_success() else 'err'
                show_file(
                        'output', 'dump',
                        case.is_dump_success(),
                        case['dump'][key]['path'],
                )

