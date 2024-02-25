#!/usr/bin/env python3

import nestedtext as nt
from voluptuous import Schema, Coerce, MultipleInvalid
from voluptuous_errors import report_voluptuous_errors
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

def normalize_key(key, parent_keys):
    return '_'.join(key.lower().split())

filename = "deploy.nt"
try:
    keymap = {}
    raw = nt.load(filename, keymap=keymap, normalize_key=normalize_key)
    config = schema(raw)
except nt.NestedTextError as e:
    e.terminate()
except MultipleInvalid as e:
    report_voluptuous_errors(e, keymap, filename)
    terminate()

pprint(config)
