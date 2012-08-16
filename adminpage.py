# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db

from common import *
from myclass import *
from mainpage import *

import time

def output_admin(out, sites):
	output_html_header(out)
	out.write("<body style='margin: 20px 60px 20px 60px;font-size:13px;'>\n")

	user = users.get_current_user()
	greeting = ("Hi, %s ( <a href=\"%s\">sign out</a> )" %
		    (user.nickname(), users.create_logout_url("/")))
	out.write("<div style='margin:-15px -55px 0 0; padding:0; text-align:right;'>" + greeting + "</div>")

	out.write("<h2 style='text-align:center'>更新リスト管理画面</h2>\n")

	out.write("<h3 style='margin-bottom:0px;'>新規追加</h3>\n")
	out.write("<div style='background-color:#EEEEEE; padding: 15px;font-size:13px;'>\n");
	out.write("<table style='font-size:12px;'>\n");
	out.write("<form action='admin' method='post'>\n")
	out.write("<input type='hidden' name='mode' value='add'/>")
	out.write("<tr><td>サイト名</td><td>：</td><td><input type='text' size='100' name='name'/></td><td>例）うにょらー</td></tr>\n")
	out.write("<tr><td>URL</td><td>：</td><td><input type='text' size='100' name='url'/></td><td>例）http://unyora.seesaa.net/</td></tr>\n")
	out.write("<tr><td colspan='3'><input type='submit' value='追加'/></td></tr>\n")
	out.write("</form>\n")
	out.write("</table>\n")
	out.write("<p>※ 対応ブログ：seesaa, hatena, goo, shinobi, blogspot, fc2, ameblo, so-net, livedoor, cocolog, love.ap.teacup.com</p>")
	out.write("</div>")
	
	out.write("<h3 style='margin-bottom:0px;'>登録サイト一覧</h3>\n")
	out.write("<div style='background-color:#EEEEEE; padding: 15px;'>\n")

	out.write("<table style='width:100%;font-size:13px;'>\n")
	for site in sites:	
		out.write("<tr>\n")
		out.write("<td>・ " + site.name.encode('utf-8') + "</td><td>" + site.url.encode('utf-8') + "</td>\n")
		if( site.time_update == None ):
			out.write("<td><span style='font-weight:bold;color:red'>NG</span></td>\n")
		else:
			year, mon, mday, hour, min, sec, wday = parse_time(time.localtime(site.time_update))
			out.write("<td><span style='font-weight:bold;color:blue;'>OK</span> -&gt; %04d/%02d/%02d(%s) %02d:%02d:%02d</td>\n"
				  % (year, mon, mday, WDAYS[wday], hour, min, sec))
		out.write("<td><form action='./admin' method='post' style='margin:0px;padding:0px'>\n")
		out.write("<input type='hidden' name='mode' value='delete'/>\n")
		out.write("<input type='hidden' name='key' value='" + str(site.key()) + "'/>\n")
		out.write("<input type='submit' value='削除'/>\n")
		out.write("</form></td>\n")
		out.write("</tr>\n")

	out.write("</div>\n")

	out.write("</body>\n")
	output_html_footer(out)

class AdminPage(webapp.RequestHandler):
	def get(self):

		sites = get_all_sites_order_by_name()

		self.response.headers['Content-Type'] = 'text/html'
		output_admin(self.response.out, sites)

		
	def post(self):
		
		mode = self.request.get("mode")
		
		if( mode == 'add' ):
			# get parameters
			site_name = self.request.get('name')
			site_url = self.request.get('url')

			# create Site entity
#			site = Site(name=site_name,url=site_url)
			site = Site.get_or_insert(site_url,name=site_name,url=site_url)
			site.put()

			# update time_update
			get_update_time(site)

		elif( mode == 'delete' ):
			# get parameter
			key = self.request.get('key')
			
			# get site and active change to False
			site = Site.get(key)
			site.delete()

		# show admin page
		sites = get_all_sites_order_by_name()

		self.response.headers['Content-Type'] = 'text/html'
		output_admin(self.response.out, sites)
