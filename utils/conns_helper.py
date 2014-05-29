# encoding: utf-8
# Created on 2014-5-13
# @author: binge

import sys
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from utils.common import RedisStrHelper
import redis
from settings import redis_def_db, redis_host, redis_port, mongo_host, \
    mongo_port, spider_redis_queues, crawling_key_prefix, crawling_key_expire, \
    redis_sep, last_crawl_time_key, celery_task_info_key
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
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def get_info_from_home_queue(spider_name, rconn=None):
        info = rconn.lpop(spider_redis_queues[spider_name])
        crawling_key = crawling_key_prefix + info
        if rconn.exists(crawling_key):
            return None
        rconn.setex(crawling_key, '1', crawling_key_expire)
        return info, info.split(redis_sep)[1]

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def pop_home_crawl_info(spider_name, rconn=None):
        return rconn.lpop(spider_redis_queues[spider_name])

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def get_last_crawl_time(spider_name, rconn=None):
        '''
            get spider(which named by parameter spider_name) the last crawled time.
        '''
        return rconn.hget(last_crawl_time_key, spider_name)

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def set_next_crawl_time(spider_name, time, rconn=None):
        '''
            set spider(which named by parameter spider_name) the next crawl time.
        '''
        rconn.hset(last_crawl_time_key, spider_name, time)

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def set_crawling_home(crawl_info, rconn=None):
        '''
            set crawling home page and expire it.
        '''
        crawling_key = crawling_key_prefix + crawl_info
        rconn.setex(crawling_key, '1', crawling_key_expire)

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def exists_crawling_home(crawl_info, rconn=None):
        '''
            judge crawling home page is crawling or not.
        '''
        crawling_key = crawling_key_prefix + crawl_info
        return rconn.exists(crawling_key)

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def del_crawling_home(crawl_info, rconn=None):
        '''
            delete crawling home page.
        '''
        crawling_key = crawling_key_prefix + crawl_info
        rconn.delete(crawling_key)

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def set_celery_task_info(res_id, spider_name, status='PENGING', rconn=None, **kwargs):
        rconn.hset(celery_task_info_key, res_id, RedisStrHelper.contact(status, spider_name, **kwargs))

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def get_all_celery_tasks_info(rconn=None):
        return rconn.hgetall(celery_task_info_key)

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def update_celery_task_status(res_id, status, rconn=None):
        val = rconn.hget(celery_task_info_key, res_id)
        vs = RedisStrHelper.split(val)
        vs[0] = status
        rconn.hsetnx(celery_task_info_key, res_id, RedisStrHelper.contact(vs))

    @staticmethod
    @redis_exec(rconn = RedisHelper.get_redis_conn())
    def del_celery_task_status(res_id, rconn=None):
        rconn.hdel(celery_task_info_key, res_id)

class MongoHelper():

    @staticmethod
    def get_mongo():
        return pymongo.Connection(mongo_host, mongo_port)

    @staticmethod
    def close_mongo(mongo):
        if mongo:
            mongo.close()

def redis_exec(redis):
    def wrapper(fn):
        def _exec():
            try:
                return fn(redis)
            except:
                raise Exception(traceback.format_exc())
            finally:
                RedisHelper.close_redis_conn(redis)
        return _exec
    return wrapper

def mongo_exec(mongo):
    def wrapper(fn):
        def _exec():
            try:
                return fn(mongo)
            except:
                raise Exception(traceback.format_exc())
            finally:
                MongoHelper.close_mongo(mongo)
        return _exec
    return wrapper
