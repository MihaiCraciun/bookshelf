# encoding: utf-8
# Created on 2014-5-7
# @author: binge

import sys
import datetime
from bookshelf.settings import last_crawl_time_prefix, redis_def_db, redis_host,\
    redis_port, crawling_key_prefix, crawling_key_expire, mongo_host, mongo_port
import redis
import pymongo
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

def get_redis_conn():
    return redis.Redis(host=redis_host, port=redis_port, db=redis_def_db)

def close_redis_conn(rconn):
    if rconn:
        del rconn

def get_mongo():
    return pymongo.Connection(mongo_host, mongo_port)

def close_mongo(mongo):
    if mongo:
        mongo.close()

def time_2_str(time = datetime.datetime.now(), frt = '%Y-%m-%d %H:%M:%S'):
    '''
        this function parse time obj to str by frt parameter,
        parameter time is default datetime.datetime.now(),
        and parameter frt default %Y-%m-%d %H:%M:%S
    '''
    return time.strftime(frt)

def get_last_crawl_time(spider_name):
    '''
        get spider(which named by parameter spider_name) the last crawled time.
    '''
    key = last_crawl_time_prefix + spider_name
    rconn = None
    try:
        rconn = get_redis_conn()
        return rconn.get(key)
    finally:
        close_redis_conn(rconn)

def set_next_crawl_time(spider_name, time):
    '''
        set spider(which named by parameter spider_name) the next crawl time.
    '''
    key = last_crawl_time_prefix + spider_name
    rconn = None
    try:
        rconn = get_redis_conn()
        rconn.set(key, time)
    finally:
        close_redis_conn(rconn)

def set_crawling_home(crawl_info):
    '''
        set crawling home page and expire it.
    '''
    crawling_key = crawling_key_prefix + crawl_info
    rconn = None
    try:
        rconn = get_redis_conn()
        rconn.setex(crawling_key, '1', crawling_key_expire)
    finally:
        close_redis_conn(rconn)

def exists_crawling_home(crawl_info):
    '''
        judge crawling home page is crawling or not.
    '''
    crawling_key = crawling_key_prefix + crawl_info
    rconn = None
    try:
        rconn = get_redis_conn()
        return rconn.exists(crawling_key)
    finally:
        close_redis_conn(rconn)

def del_crawling_home(crawl_info):
    '''
        delete crawling home page.
    '''
    crawling_key = crawling_key_prefix + crawl_info
    rconn = None
    try:
        rconn = get_redis_conn()
        rconn.delete(crawling_key)
    finally:
        close_redis_conn(rconn)
