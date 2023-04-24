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

try:
    keymap = {}
    raw = nt.load('deploy.nt', keymap=keymap)
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
        loc = keymap[tuple(e.path)]
        error(full_stop(msg), culprit=e.path, codicil=loc.as_line(flag))
    terminate()

pprint(config)
