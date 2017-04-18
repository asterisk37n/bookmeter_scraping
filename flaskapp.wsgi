#!/usr/bin/myenv python
# -*- coding: UTF-8 -*-
import site
import sys

site.addsitedir('/usr/bin/myenv/lib64/python3.4/site-packages')
sys.path.append('/var/www/html/flaskapp')
activate_this = '/usr/bin/myenv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
import sys
sys.path.insert(0, '/var/www/html/bookmeter_scraping')

from flaskapp import app as application
