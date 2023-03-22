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

# provide user-friendly error messages
voluptuous_error_msg_mappings = {
    "extra keys not allowed": ("unknown key", "key"),
    "expected a dictionary": ("expected key-value pairs", "value"),
}

try:
    keymap = {}
    raw = nt.load('deploy.nt', keymap=keymap)
    config = schema(raw)
except nt.NestedTextError as e:
    e.terminate()
except MultipleInvalid as e:
    for err in e.errors:
        msg, flag = voluptuous_error_msg_mappings.get(
            err.msg, (err.msg, 'value')
        )
        loc = keymap[tuple(err.path)]
        error(full_stop(msg), culprit=err.path, codicil=loc.as_line(flag))
    terminate()

pprint(config)
