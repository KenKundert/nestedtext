#!/usr/bin/env python3

import nestedtext as nt
from voluptuous import Schema, Coerce
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
raw = nt.load('deploy.nt')
config = schema(raw)

pprint(config)
