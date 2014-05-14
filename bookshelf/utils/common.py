# encoding: utf-8
# Created on 2014-5-7
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import datetime
from bookshelf.settings import source_spider_sleep_secs, redis_sep, \
    source_home_spiders, every_crawl_timedelta_mins
import time
import lxml.etree;

delta_time_dict = {
                   'microseconds': lambda t, delta : t + datetime.timedelta(microseconds=delta),
                   'milliseconds': lambda t, delta : t + datetime.timedelta(milliseconds=delta),
                   'seconds' : lambda t, delta : t + datetime.timedelta(seconds=delta),
                   'minutes' : lambda t, delta : t + datetime.timedelta(minutes=delta),
                   'hours' : lambda t, delta : t + datetime.timedelta(hours=delta),
                   'days' : lambda t, delta : t + datetime.timedelta(days=delta),
                   'weeks' : lambda t, delta : t + datetime.timedelta(weeks=delta)
                   }

def time_2_str(t=datetime.datetime.now(), frt='%Y-%m-%d %H:%M:%S', delta=None, delta_unit=None):
    '''
        this function parse time obj to str by frt parameter,
        parameter t is default datetime.datetime.now(),
        and parameter frt default %Y-%m-%d %H:%M:%S.
        delta_unit:
                    seconds
                    minutes
                    hours
                    days
                    ...
    '''
    if delta and delta_unit:
        t = delta_time_dict[delta_unit](t, delta)
    return t.strftime(frt)

def sleep(seconds):
    time.sleep(seconds)

def source_spider_sleep():
    time.sleep(source_spider_sleep_secs)

def split_redis_str(s):
    return s.split(redis_sep)

def contact_redis_str(*kwagrs):
    if kwagrs:
        s = ''
        for arg in kwagrs:
            s += arg + redis_sep
        return s[:-len(redis_sep)]
    else:
        return ''

def get_source_home_spider(spider_name):
    return source_home_spiders[spider_name]

def get_every_crawl_timedelta_mins():
    return every_crawl_timedelta_mins

def create_dom(data, parser=None):
    if not parser:
        parser = lxml.etree.HTMLParser()
    return lxml.etree.fromstring(data, parser);
