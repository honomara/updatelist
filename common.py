# -*- coding: utf-8 -*-

import random
import time

VERSION = '3.1'

def get_jst_time(t = None):
	if t == None:
		t = int(time.time())
	return time.localtime(t + (9 * 3600))

def get_random_query_string():
	random.seed(int(time.time()))
	random_query_string = "q=" + str(random.random())
	return "?q=" + str(random.random())

def parse_time(t):
	return t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, t.tm_wday

def qsort(sites):
        if len(sites) <= 1:
                return sites
        pivot = sites.pop(0)
        greater_eq = qsort([i for i in sites if i.time >= pivot.time])
        lesser = qsort([i for i in sites if i.time < pivot.time])
        return greater_eq + [pivot] + lesser

def output_html_header(out):
        out.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        out.write('<html lang="ja">\n')
        out.write('\n')
        out.write('<head>\n')
        out.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n')
        out.write('<title>更新リスト ' + VERSION + '</title>\n')
        out.write('</head>\n')
        out.write('\n')

def output_html_footer(out):
        out.write('</html>\n')

