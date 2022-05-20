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
except MultipleInvalid as e:
    for err in e.errors:
        kind = 'key' if 'key' in err.msg else 'value'
        loc = keymap[tuple(err.path)]
        error(full_stop(err.msg), culprit=err.path, codicil=loc.as_line(kind))
    terminate()

pprint(config)
