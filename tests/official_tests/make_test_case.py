#!/usr/bin/env python3

"""\
Helper script to quickly create test cases.

Usage:
    make_test_case.py <family> <template> [options]

Arguments:
    <family>
        The first part of the test case name, e.g. "dict", "string", etc.  A 
        number will be added to the end of this prefix to create a unique test 
        id.

    <template>
        The name of the template (i.e. one of the directories in templates/) 
        that will be used to populate the test case.  You will be prompted to 
        edit every non-symlink file in this directory.  Below are the files 
        created by the available templates:

{}

Options:
    -r --readme
        Include a `README` in the test case.  This is useful if you want to 
        highlight a unique or subtle feature of the test.

    -n --num <int>
        Append the given number to the above family name rather than 
        automatically picking the next consecutive number.  Note that this 
        doesn't actually have to be a number, e.g. you could specify "2a" to 
        make a new test that will go between "2" and "3" after renumbering.

    -e --editor <path>
        The editor to use to edit the test case files.  The default is to use 
        the value of the $EDITOR environment variable, or `vim` if that 
        variable is undefined.
"""

import os, re, docopt, shutil
from pathlib import Path
from subprocess import run
from inform import fatal
from textwrap import indent

ROOT_DIR = Path(__file__).parent
CASE_DIR = ROOT_DIR / 'test_cases'
TEMPLATE_DIR = ROOT_DIR / 'templates'
TEMPLATE_ORDER = {
        x: i
        for i,x in enumerate([
            'l',
            'ld',
            'lD',
            'le',
            'd',
            'de',
        ])
}
FILE_ORDER = {
        x: i
        for i, x in enumerate([
            'README',
            'load_in.nt',
            'load_out.json',
            'load_err.json',
            'dump_in.nt',
            'dump_out.json',
            'dump_err.json',
        ])
}

def name_test_dir(prefix, num):
    if num is None:
        max_num = 0
        for path in CASE_DIR.iterdir():
            if m := re.fullmatch(f'{prefix}_(\d+)', path.name):
                max_num = max(max_num, int(m.group(1)))
        num = max_num + 1

    return CASE_DIR / f'{prefix}_{num}'

def document_templates():
    doc = ""
    template_dirs = sorted(
            TEMPLATE_DIR.iterdir(),
            key=lambda p: TEMPLATE_ORDER.get(p.name, len(TEMPLATE_ORDER))
    )

    for dir in template_dirs:
        doc += f"{dir.name}:\n"

        for path in sorted(
                dir.iterdir(),
                key=lambda p: FILE_ORDER.get(p.name, len(FILE_ORDER)),
        ):
            notes = ""
            if path.is_symlink():
                notes = f" (symlink to {path.resolve().name})"

            doc += f"  {path.name}{notes}\n"

    return doc.strip()


if __name__ == '__main__':
    template_docs = document_templates()
    args = docopt.docopt(__doc__.format(indent(template_docs, 8*' ')))
    case = name_test_dir(args['<family>'], args['--num'])
    template = TEMPLATE_DIR / args['<template>']

    if not template.is_dir():
        fatal("template not found", culprit=template.name)

    shutil.copytree(template, case, symlinks=True)
    print(case)

    if args['--readme']:
        readme = case / 'README'
        readme.touch()

    editor = args['--editor'] or os.environ.get('EDITOR', 'vim')
    editor_args = [
            str(p)
            for p in sorted(
                case.iterdir(),
                key=lambda p: FILE_ORDER.get(p.name, len(FILE_ORDER)),
            )
            if p.is_file() and not p.is_symlink()
    ]
    run([editor, *editor_args])
