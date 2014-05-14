# encoding: utf-8
# Created on 2014-5-7
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import datetime
from bookshelf.settings import source_home_spiders, every_crawl_timedelta_mins,\
    redis_sep
import time
import lxml.etree;

class TimeHelper():

    @staticmethod
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
            delta_time_dict = {
                               'microseconds': lambda t, delta : t + datetime.timedelta(microseconds=delta),
                               'milliseconds': lambda t, delta : t + datetime.timedelta(milliseconds=delta),
                               'seconds' : lambda t, delta : t + datetime.timedelta(seconds=delta),
                               'minutes' : lambda t, delta : t + datetime.timedelta(minutes=delta),
                               'hours' : lambda t, delta : t + datetime.timedelta(hours=delta),
                               'days' : lambda t, delta : t + datetime.timedelta(days=delta),
                               'weeks' : lambda t, delta : t + datetime.timedelta(weeks=delta)
                               }
            t = delta_time_dict[delta_unit](t, delta)
        return t.strftime(frt)

class SpiderHelper():

    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)

    @staticmethod
    def source_spider_sleep():
        time.sleep(60 * 10)

    @staticmethod
    def get_source_home_spider(spider_name):
        return source_home_spiders[spider_name]

    @staticmethod
    def get_every_crawl_timedelta_mins():
        return every_crawl_timedelta_mins

class RedisStrHelper():

    @staticmethod
    def split(s):
        return s.split(redis_sep)

    @staticmethod
    def contact(*kwargs):
        if kwargs:
            s = ''
            for arg in kwargs:
                s += arg + redis_sep
            return s[:-len(redis_sep)]
        else:
            return ''

def create_dom(data, parser=None):
    if not parser:
        parser = lxml.etree.HTMLParser()
    return lxml.etree.fromstring(data, parser);
