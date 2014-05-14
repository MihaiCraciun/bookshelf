# encoding: utf-8
# Created on 2014-5-13
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import redis
from bookshelf.settings import redis_def_db, redis_host, redis_port, mongo_host, \
    mongo_port, spider_redis_queues, crawling_key_prefix, crawling_key_expire, \
    redis_sep, last_crawl_time_key
import pymongo

class RedisHelper():

    @staticmethod
    def get_redis_conn():
        return redis.Redis(host=redis_host, port=redis_port, db=redis_def_db)

    @staticmethod
    def close_redis_conn(rconn):
        if rconn:
            del rconn

    @staticmethod
    def get_info_from_home_queue(spider_name):
        rconn = None
        try:
            rconn = RedisHelper.get_redis_conn()
            info = rconn.lpop(spider_redis_queues[spider_name])
            crawling_key = crawling_key_prefix + info
            if rconn.exists(crawling_key):
                return None
            rconn.setex(crawling_key, '1', crawling_key_expire)
            return info, info.split(redis_sep)[1]
        finally:
            RedisHelper.close_redis_conn(rconn)

    @staticmethod
    def pop_home_crawl_info(spider_name):
        rconn = None
        try:
            rconn = RedisHelper.get_redis_conn()
            return rconn.lpop(spider_redis_queues[spider_name])
        finally:
            RedisHelper.close_redis_conn(rconn)

    @staticmethod
    def get_last_crawl_time(spider_name):
        '''
            get spider(which named by parameter spider_name) the last crawled time.
        '''
        rconn = None
        try:
            rconn = RedisHelper.get_redis_conn()
            return rconn.hget(last_crawl_time_key, spider_name)
        finally:
            RedisHelper.close_redis_conn(rconn)

    @staticmethod
    def set_next_crawl_time(spider_name, time):
        '''
            set spider(which named by parameter spider_name) the next crawl time.
        '''
        rconn = None
        try:
            rconn = RedisHelper.get_redis_conn()
            rconn.hset(last_crawl_time_key, spider_name, time)
        finally:
            RedisHelper.close_redis_conn(rconn)

    @staticmethod
    def set_crawling_home(crawl_info):
        '''
            set crawling home page and expire it.
        '''
        crawling_key = crawling_key_prefix + crawl_info
        rconn = None
        try:
            rconn = RedisHelper.get_redis_conn()
            rconn.setex(crawling_key, '1', crawling_key_expire)
        finally:
            RedisHelper.close_redis_conn(rconn)

    @staticmethod
    def exists_crawling_home(crawl_info):
        '''
            judge crawling home page is crawling or not.
        '''
        crawling_key = crawling_key_prefix + crawl_info
        rconn = None
        try:
            rconn = RedisHelper.get_redis_conn()
            return rconn.exists(crawling_key)
        finally:
            RedisHelper.close_redis_conn(rconn)

    @staticmethod
    def del_crawling_home(crawl_info):
        '''
            delete crawling home page.
        '''
        crawling_key = crawling_key_prefix + crawl_info
        rconn = None
        try:
            rconn = RedisHelper.get_redis_conn()
            rconn.delete(crawling_key)
        finally:
            RedisHelper.close_redis_conn(rconn)

class MongoHelper():

    @staticmethod
    def get_mongo():
        return pymongo.Connection(mongo_host, mongo_port)

    @staticmethod
    def close_mongo(mongo):
        if mongo:
            mongo.close()


