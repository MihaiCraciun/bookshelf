# encoding: utf-8
# Created on 2014-5-7
# @author: binge

import sys
import datetime
from bookshelf.settings import last_crawl_time_prefix, redis_def_db, redis_host,\
    redis_port
import redis
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

def time_2_str(time = datetime.datetime.now(), frt = '%Y-%m-%d %H:%M:%S'):
    '''
        this function parse time obj to str by frt parameter,
        parameter time is default datetime.datetime.now(),
        and parameter frt default %Y-%m-%d %H:%M:%S
    '''
    return time.strftime(frt)

def get_last_crawl_time(spider_name):
    key = last_crawl_time_prefix + spider_name
    rconn = redis.Redis(host=redis_host, port=redis_port, db=redis_def_db)
    try:
        return rconn.get(key)
    finally:
        del rconn

def set_next_crawl_time(spider_name, time):
    key = last_crawl_time_prefix + spider_name
    rconn = redis.Redis(host=redis_host, port=redis_port, db=redis_def_db)
    try:
        rconn.set(key, time)
    finally:
        del rconn
