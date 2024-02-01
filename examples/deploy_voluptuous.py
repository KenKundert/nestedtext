#!/usr/bin/env python3

import nestedtext as nt
from voluptuous import Schema, Coerce, MultipleInvalid
from inform import error, full_stop, terminate
from pprint import pprint

schema = Schema({
    'debug': Coerce(bool),
    'secret_key': str,
    'allowed_hosts': [str],
    'database': {
        'engine': str,
        'host': str,
        'port': Coerce(int),
        'user': str,
    },
    'webmaster_email': str,
})

filename = "deploy.nt"
try:
    keymap = {}
    raw = nt.load(filename, keymap=keymap)
    config = schema(raw)
except nt.NestedTextError as e:
    e.terminate()
except MultipleInvalid as exception:
    voluptuous_error_messages = {  # provide user-friendly error messages
        "extra keys not allowed": ("unknown key", "key"),
        "expected a dictionary": ("expected key-value pair", "value"),
    }
    for e in exception.errors:
        msg, flag = voluptuous_error_messages.get(
            e.msg, (e.msg, 'value')
        )
        culprit = nt.join_keys(e.path, keymap=keymap, sep="/")
        loc = keymap.get(tuple(e.path))
        if loc:
            codicil = loc.as_line(flag)
            line_num, col_num = loc.as_tuple(flag)
            source = f"{filename!s}@{line_num+1}"
        else:  # required key is missing
            codicil = None
            source = str(filename)

        error(full_stop(msg), culprit=(source, culprit), codicil=codicil)
    terminate()

pprint(config)
