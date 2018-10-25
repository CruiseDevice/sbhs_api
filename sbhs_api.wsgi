#!/usr/bin/python

activate_this = '/path/to/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/path/to/sbhs_api/")
sys.path.insert(1,"/path/to/venv/")

from sbhs_server import app as application
application.secret_key = 'your secret application key'
