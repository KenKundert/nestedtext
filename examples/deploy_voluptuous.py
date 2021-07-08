#!/usr/bin/env python3

import nestedtext as nt
from voluptuous import Schema, Coerce, Invalid
from inform import fatal, full_stop
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
except Invalid as e:
    kind = 'key' if 'key' in e.msg else 'value'
    loc = keymap[tuple(e.path)]
    fatal(full_stop(e.msg), culprit=e.path, codicil=loc.as_line(kind))

pprint(config)
