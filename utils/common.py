# encoding: utf-8
# Created on 2014-5-7
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import datetime
from settings import source_home_spiders, every_crawl_timedelta_mins,\
    redis_sep, source_spider_sleep_secs, search_spider_names,\
    book_no_home_url_val
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
        time.sleep(source_spider_sleep_secs)

    @staticmethod
    def get_source_home_spider(spider_name):
        return source_home_spiders[spider_name]

    @staticmethod
    def get_every_crawl_timedelta_mins():
        return every_crawl_timedelta_mins

    @staticmethod
    def get_sea_result_home_spider(sea_spider_name):
        for home_spider in search_spider_names:
            if search_spider_names[home_spider] == sea_spider_name:
                return home_spider

class RedisStrHelper():

    @staticmethod
    def split(s):
        return s.split(redis_sep)

    @staticmethod
    def contact(*kwargs, **kwparas):
        s = ''
        if kwargs:
            for arg in kwargs:
                if not arg is None:
                    if arg.__class__ is list:
                        for a in arg:
                            s += str(a) + redis_sep
                    else:
                        s += str(arg) + redis_sep
        if kwparas:
            for k in kwparas:
                if not kwparas[k] is None:
                    if kwparas[k].__class__ is list:
                        for b in kwparas[k]:
                            s += str(b) + redis_sep
                    else:
                        s += str(kwparas[k]) + redis_sep
        if s:
            return s[:-len(redis_sep)]
        else:
            return s

def create_dom(data, parser=None):
    if not parser:
        parser = lxml.etree.HTMLParser()  # @UndefinedVariable
    return lxml.etree.fromstring(data, parser);  # @UndefinedVariable

class SettingsHelper():

    @staticmethod
    def get_book_no_home_url_val():
        return book_no_home_url_val
