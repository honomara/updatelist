# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext import db

from httplib import HTTPConnection, HTTPException, HTTPSConnection

from common import *
from myclass import *

import logging, re

CACHE_LIFETIME    = 600
HTTP_TIMEOUT      = 3
PAGE_SIZE         = 4096
WDAYS             = ['月', '火', '水', '木', '金', '土', '日']

#############################################
# If you add site type, add to this fuction #
#############################################
def parse_url(url):
	
	# goo
	if( url.find('blog.goo.ne.jp') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url) + 'index.rdf'
		type = 2
		tag = '<dc:date>'
		ssl = False
	# livedoor
	elif( url.find('blog.livedoor.jp') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url) + 'index.rdf'
		type = 2
		tag = '<dc:date>'
		ssl = False
	# google
	elif( url.find('sites.google.com') >= 0 ):
		host = 'sites.google.com'
		path = '/feeds/content' + get_default_path(url)
		type = 5
		tag = ''
		protocol = 'http'
		ssl = True
	# Seesaa
	elif( url.find('.seesaa.net') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url ) + 'index.rdf'
		type = 2
		tag = '<dc:date>'
		ssl = False
	# hatena
	elif( url.find('d.hatena.ne.jp') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url ) + 'rss'
		type = 2
		tag = '<dc:date>'
		ssl = False
	# shinobi
	elif( url.find('.blog.shinobi.jp') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url ) + 'atom'
		type = 2
		tag = '<dc:date>'
		ssl = False
	# blogspot
	elif( url.find('.blogspot.com') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url ) + 'rss.xml'
		type = 2
		tag = '<updated>'
		ssl = False
	# fc2
	elif( url.find('.fc2.com') >= 0 ):
		host = "feeds.fc2.com"
		path = "/fc2/xml?host=" + get_default_host(url).replace(".fc2.com", "")
		type = 2
		tag = '<dc:date>'
		ssl = False
	# ameblo
	elif( url.find('ameblo.jp') >= 0 ):
		host = "feedblog.ameba.jp"
		path = "/rss/ameblo" + get_default_path(url) + "rss20.xml"
		type = 2
		tag = '<pubDate>'
		ssl = False
	# yahoo
	elif( url.find('blogs.yahoo.co.jp') >= 0):
		host = get_default_host(url)
		path = get_default_path(url) + 'rss.xml'
		type = 2
		tag = '<pubDate>'
		ssl = False
	# cocolog
	elif( url.find('cocolog-nifty.com') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url) + "index.rdf"
		type = 2
		tag = '<dc:date>'
		ssl = False
	# so-net
	elif( url.find('.blog.so-net.ne.jp') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url) + "atom.xml"
		type = 2
		tag = '<modified>'
		ssl = False
	# love.ap.teacup.com
	elif( url.find('love.ap.teacup.com') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url) + "rss.xml"
		type = 2
		tag = '<dc:date>'
		ssl = False
	# Honomara OB
	elif( url.find('ob.honomara.net/bbs') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url)
		type = 3
		tag  = ''
		ssl = False
	elif( url.find('ob.honomara.net/luna') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url) + "last_modified.txt"
		type = 4
		tag  = ''
		ssl = False
	# Honomara
	elif( url.find('.honomara.net/cgi-bin/wiki') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url) + "index.php?cmd=rss&ver=1.0"
		type = 2
		tag  = '<dc:date>'
		ssl = False
	elif( url.find('.honomara.net') >= 0 ):
		host = get_default_host(url)
		path = get_default_path(url)
		type = 0
		tag  = ''
		ssl = False
	# others
	else:
		host = get_default_host(url)
		path = get_default_path(url)
		type = 1
		tag  = '' 
		ssl = False
		
	return host,path,type,tag,ssl


def get_update_time_0(site):
        global HTTP_TIMEOUT

	# get site parameters
	host, path, type, tag, ssl = parse_url(site.url)

        httpcon = HTTPConnection('www.honomara.net', 80, timeout=HTTP_TIMEOUT)
        httpcon.request('GET', '/etc/list.php', {}, {})
        res = httpcon.getresponse()
        for line in res.read().split('\n'):
                if line == '': break
                tokens = line.split('\t')
		if ('http://' + host + path) == tokens[1]:
			time_update = time.strptime(tokens[2], '%y%m%d%H%M%S')
			update_update_time(site, time_update)

        httpcon.close()

def get_update_time_1(site):
        global HTTP_TIMEOUT

	# get site parameters
	host, path, type, tag, ssl = parse_url(site.url)

        httpcon = HTTPConnection(host, 80, timeout=HTTP_TIMEOUT)
        httpcon.request('HEAD', path, {}, {})
        res = httpcon.getresponse()
        for pair in res.getheaders():
                if pair[0] == 'last-modified':
			time_str = pair[1]
                        time_update = time.strptime(time_str[5:25], '%d %b %Y %H:%M:%S')
#                        time_update = time.strptime(pair[1], '%a, %d %b %Y %H:%M:%S %Z')
                        time_update = time.localtime(time.mktime(time_update) + 9*3600)
			update_update_time(site, time_update)

        httpcon.close()

def get_update_time_2(site):
        global HTTP_TIMEOUT, PAGE_SIZE

	# get site parameters
	host, path, type, tag, ssl = parse_url(site.url)

	if ssl:
		httpcon = HTTPSConnection(host)
	else:
		httpcon = HTTPConnection(host, 80, timeout=HTTP_TIMEOUT)
        httpcon.request('GET', path, {}, {})
        res = httpcon.getresponse()

        # look for tag in the first 4096 bytes
        body = res.read(PAGE_SIZE)
        index = body.find(tag)

        # look at the remaining bytes only if necessary
        if (index == -1):
                body += res.read()
                index = body.find(tag)

	# if tag found, make close tag str and look for
	if( index >= 0 ):
		close_tag = tag.replace("<","</")
		close_tag_index = body.find(close_tag)

	# if close-tag found, get time repesentation
	if( close_tag_index >= 0 ):
		time_str = body[index+len(tag):close_tag_index]

		if( tag == '<pubDate>' ): # for ameblo and yahoo
			time_update = time.strptime(time_str[5:25], '%d %b %Y %H:%M:%S')
		else:
			time_update = time.strptime(time_str[0:19], '%Y-%m-%dT%H:%M:%S')

		update_update_time(site, time_update)

        httpcon.close()

def get_update_time_3(site):
        global HTTP_TIMEOUT

	# get site parameters
	host, path, type, tag, ssl = parse_url(site.url)

        httpcon = HTTPConnection(host, 80, timeout=HTTP_TIMEOUT)
        httpcon.request('GET', path, {}, {})
        res = httpcon.getresponse()

        for line in res.read().split('\n'):
                m = re.search('([0-9]{4})...([0-9]{1,2})...([0-9]{1,2})...\(...\) ([0-9]{2}):([0-9]{2})</span>\Z', line)
                if m is not None:
                        time_str = '%s/%s/%s %s:%s' % m.groups()
                        time_update = time.strptime(time_str, '%Y/%m/%d %H:%M')
                        if time.mktime(time_update) > site.time_update:
				update_update_time(site, time_update)

        httpcon.close()

def get_update_time_4(site):
        global HTTP_TIMEOUT

        httpcon = HTTPConnection('ob.honomara.net', 80, timeout=HTTP_TIMEOUT)
#        httpcon = HTTPConnection('127.0.0.1', 80, timeout=HTTP_TIMEOUT)
        httpcon.request('GET', '/luna/last_modified.txt', {}, {})
        res = httpcon.getresponse()
 
        time_update = time.strptime(res.read(), '%y%m%d%H%M%S')
	update_update_time(site, time_update)

        httpcon.close()

def get_update_time_5(site):
	# TO-DO: merge this function into get_update_time_2

	global HTTP_TIMEOUT, PAGE_SIZE

	# get site parameters
	host, path, type, tag, ssl = parse_url(site.url)

	httpcon = HTTPSConnection(host)
	httpcon.request('GET', path, {}, {})
	res = httpcon.getresponse()

	# look for tag in the first 4096 bytes
	body = res.read()
	index = body.find("</published><updated>")

	# TO-DO: look at the remaining bytes if necessary

	# if tag found, look for close tag
	if ( index >= 0 ):
		close_tag = "</updated>"
		close_tag_index = index + body[index:].find(close_tag)

	# if close tag found, get time representation
	if ( close_tag_index >= 0 ):
		time_str = body[index+len("</published><updated>"):close_tag_index]

		# parse time string and add 32400 secs to make JST
		time_update_uct = time.strptime(time_str[0:19], '%Y-%m-%dT%H:%M:%S')
		time_update = time.localtime(time.mktime(time_update_uct) + 32400)

		update_update_time(site, time_update)

	httpcon.close()

def get_default_host(url):
	tokens = url.split('/')
	return tokens[2]

def get_default_path(url):
	tokens = url.split('/')
	return '/' + '/'.join(tokens[3:])

def get_site_type(site):
	host, path, type, tag, ssl = parse_url(site.url)
	return type

def get_update_time(site):

	# reset time_check, time_update
	site.time_check = None
	site.time_update = None
	
	# get site type
	type = get_site_type(site)

	# get update time
	try:
		if type == 0:
			get_update_time_0(site)
		elif type == 1:
			get_update_time_1(site)
		elif type == 2:
			get_update_time_2(site)
		elif type == 3:
			get_update_time_3(site)
		elif type == 4:
			get_update_time_4(site)
		elif type == 5:
			get_update_time_5(site)
	except Exception, e:
		logging.error(e)
		logging.error("## Failed to check " + site.url)

def check_sites(sites, cron_flag):
        global CACHE_LIFETIME

	logging.info("## now                         [" + str(int(time.time())) + "]")
	logging.info("## time_cache + CACHE_LIFETIME [" + str(get_access().time_cache + CACHE_LIFETIME) + "] (= " + str(get_access().time_cache) + " + " + str(CACHE_LIFETIME) + ")")

	# cache hit
        if int(time.time()) < get_access().time_cache + CACHE_LIFETIME:

		# if cron access, dont count
		if( cron_flag != "1" ):
			increment_hit()

	# cache miss
        else:
		# update cache time
		update_cache_time()

		# get update time from each site
                for site in sites:
			logging.info("## Check [" + site.url + "]")
			get_update_time(site)

		# if cron access, dont count
		if( cron_flag != "1" ):
			increment_miss()
		

def output_html_body(out, sites):
        global WDAYS

	# get list update time
	lt = get_jst_time(get_access().time_cache)

        out.write('<body>\n')
        out.write('<div align="center">\n')
        out.write('<h2 style="margin-bottom:10px">更新リスト ' + VERSION + '</h2>\n')

        out.write('<font size="2">リスト更新日時: %02d/%02d(%s) ' % (lt.tm_mon, lt.tm_mday, WDAYS[lt.tm_wday]))
        out.write('%02d:%02d:%02d</font><br><br>\n' % (lt.tm_hour, lt.tm_min, lt.tm_sec))
        out.write('<table border="0">\n')
        for site in sites:
		
		# get site parameters
		year, mon, mday, hour, min, sec, wday = parse_time(time.localtime(site.time_update))
		site_url = site.url.encode('utf-8')
		site_name = site.name.encode('utf-8')

                out.write('<tr><td align="right"><font size="2">')
		if site.time_check == None:
                        out.write('失敗')
		elif site.time_update == None:
			out.write('不明')
		elif time.localtime(site.time_update).tm_year != get_jst_time().tm_year:
#			year, mon, mday  = parse_time(time.localtime(site.time_update))
                        out.write('%d/%02d/%02d' % (year, mon, mday))
                else:
#			year, mon, mday, hour, min, sec, wday = parse_time(time.localtime(site.time_update))
                        out.write('%02d/%02d(%s) ' % (mon, mday, WDAYS[wday]))
                        out.write('%02d:%02d:%02d' % (hour, min, sec))
                out.write('</font></td>')
                out.write('<td width="10"></td>')
                out.write('<td align="left"><font size="2">')
                out.write('<a href="%s" target="_blank">%s</a>' % (site_url, site_name))
                out.write('</font></td></tr>\n')
        out.write('</table><br/>\n')

        out.write('<font size="2"><i>2010/11/04 からのアクセス数: ')
        out.write('%d</i></font><br/>\n' % (get_access().hit + get_access().miss) )
	out.write('<br/>')
	out.write('<img src="http://code.google.com/appengine/images/appengine-noborder-120x30.gif" alt="Powered by Google App Engine" />')
        out.write('</div>\n')
        out.write('</body>\n')
        out.write('\n')

def output_html(out, sites):
        output_html_header(out)
        output_html_body(out, sites)
        output_html_footer(out)

class MainPage(webapp.RequestHandler):
	def get(self):

		cron_flag = self.request.get('cron')

		sites = get_active_sites_order_by_time_update()
		check_sites(sites, cron_flag)

		self.response.headers['Content-Type'] = 'text/html;'
		output_html(self.response.out, sites)

