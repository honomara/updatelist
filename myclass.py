# -*- coding: utf-8 -*-

from google.appengine.ext import db

import time

# Site
class Site(db.Model):
	name = db.StringProperty(required=True)
	url = db.StringProperty(required=True)
	time_update = db.IntegerProperty()
	time_check = db.IntegerProperty()

def db_update_update_time(key, time_update, time_check):
	site = db.get(key)
	site.time_update = time_update
	site.time_check = time_check
	site.put()

def update_update_time(site, time_update ):
	site.time_update = int(time.mktime(time_update))
	site.time_check = int(time.time())
	db.run_in_transaction(db_update_update_time, site.key(), int(time.mktime(time_update)), int(time.time()));

def get_active_sites_order_by_time_update():
	sites = Site.all()
	sites.order("-time_update")
        return sites

def get_all_sites_order_by_name():
	sites = Site.all()
	sites.order("name")
	return sites

# Access 
class Access(db.Model):
	time_cache = db.IntegerProperty(default=int(time.time()))
	hit        = db.IntegerProperty(default=0)
	miss       = db.IntegerProperty(default=0)

def get_access():
	access = Access.get_or_insert("access")	
	return access

def get_access_key():
	access = get_access()
	return access.key()

def db_increment_hit(key):
	access = db.get(key)
	access.hit += 1
	access.put()

def db_increment_miss(key):
	access = db.get(key)
	access.miss += 1;
	access.put()

def db_update_cache_time(key):
	access = db.get(key)
	access.time_cache = int(time.time())
	access.put()

def increment_hit():
	db.run_in_transaction(db_increment_hit, get_access_key())

def increment_miss():
	db.run_in_transaction(db_increment_miss, get_access_key())

def update_cache_time():
	db.run_in_transaction(db_update_cache_time, get_access_key())

