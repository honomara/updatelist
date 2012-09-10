# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from adminpage import *
from mainpage import *
from common import *

##################
#  Main Function #
##################

application = webapp.WSGIApplication([
		('/', MainPage),
		('/admin', AdminPage)
		],debug=True)

def main():
	run_wsgi_app(application)


# starting point
if __name__ == '__main__':
	main()

