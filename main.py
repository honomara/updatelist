# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp

from adminpage import *
from mainpage import *
from common import *

##################
#  Main Function #
##################

import webapp2

app = webapp2.WSGIApplication([('/', MainPage)])

application = webapp.WSGIApplication([
		('/', MainPage),
		('/admin', AdminPage)
		],debug=True)
