#!/usr/bin/env python3

from settings import read_settings
from inform import Error, fatal, os_error
import nestedtext as nt

try:
    settings = read_settings('example.in.nt')
    nt.dump(settings, 'example.out.nt')
except Error as e:
    e.terminate()
except OSError as e:
    fatal(os_error(e))
