# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from bookshelf.items import Book, BookDesc, Sections
from bookshelf.settings import mongo_host, mongo_port, search_spider_queues, \
    redis_sep, qd_home_spider, spider_redis_queues, redis_def_db, redis_host, \
    redis_port, unupdate_retry_queue
import pymongo
import traceback
from scrapy import log
import redis
import datetime
from bookshelf.utils import time_2_str
# import md5
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class BookShelfPipeline(object):

    def __init__(self):
        self.rconn = redis.Redis(host=redis_host, port=redis_port, db=redis_def_db)

    def process_item(self, item, spider):
        mongo = None
        try:
            # conn mongodb
            mongo = pymongo.Connection(mongo_host, mongo_port)
            db = mongo.bookshelf
            if item.__class__ is Book:  # exec Book item.
                source = item['source']
                _id = md5(source).hexdigest()  # gene _id
                book = db.books.find_one({'_id' : _id})

                if not book:  # this book has never been crawled.
                    b = dict()
                    b['_id'] = _id
                    b['name'] = item['name']
                    b['source'] = source
                    b['source_name'] = item['source_name']
                    b['author'] = item['author']
                    b['homes'] = item['homes']
                    db.books.insert(b)  # insert it to mongodb
                    # this book must be searched in other update sites.
                    for sea in search_spider_queues:
                        if not sea == item['source_spider']:
                            self.rconn.rpush(search_spider_queues[sea], _id + redis_sep + item['name'])
                    self.rconn.rpush(spider_redis_queues[item['source_spider']], _id + redis_sep + source)
                else:  # this book has been crawled once or more.
                    book_homes = book['homes']
                    for sea in search_spider_queues:
                        if (not sea == item['source_spider']):  # if this book has some update sites not crawled yet, search it.
                            if (not sea in book_homes):
                                self.rconn.rpush(search_spider_queues[sea], _id + redis_sep + item['name'])
                        if sea in book_homes:  # get all home url to crawl.
                            home_url = book_homes[sea]
                            if home_url:
                                self.rconn.rpush(spider_redis_queues[sea], _id + redis_sep + home_url)

                # push curr home link to qidian home spider queue, then the home spider will take the responsibility.
                self.rconn.rpush(spider_redis_queues[qd_home_spider], _id + redis_sep + item['source'])
            elif item.__class__ is BookDesc:
                db.books.update({"_id" : _id}, {'$set' : {"desc":item['desc']}});
            elif item.__class__ is Sections:
                book = db.books.find_one({'_id' : item['b_id']})
                source = item['source']
                is_source = False
                if source == book['source']:
                    is_source = True
                b_id = item['b_id']
                source_short_name = item['source_short_name']
                sec_docs = db.sections.find({'b_id' : b_id, 'source_short_name' : source_short_name})
                sec_raws = item['secs']
                sec_in_docs = []
                n = datetime.datetime.now()
                i = 0
                if sec_docs:
                    old_urls = set()
                    for sd in sec_docs:
                        old_urls.add(sd['url'])
                    sr_ks = sec_raws.keys()[::-1]
                    for sk in sr_ks:
                        if not sk in old_urls:
                            sec = {}
                            sec['b_id'] = b_id
                            sec['source_short_name'] = source_short_name
                            sec['source_zh_name'] = item['source_zh_name']
                            sec['url'] = sk
                            sec['name'] = sec_raws[sk]
                            sec['crawl_time'] = time_2_str(n + datetime.timedelta(seconds=i))
                            sec_in_docs.append(sec)
                            i += 1
                        else:
                            break
                else:
                    for sr in sec_raws:
                        sec = {}
                        sec['b_id'] = b_id
                        sec['source_short_name'] = source_short_name
                        sec['source_zh_name'] = item['source_zh_name']
                        sec['url'] = sr
                        sec['name'] = sec_raws[sr]
                        sec['crawl_time'] = time_2_str(n + datetime.timedelta(seconds=i))
                        sec_in_docs.append(sec)
                        i += 1
                if not sec_in_docs and not is_source: # current executing a update site, no doc to update, push info back to redis and retry.
                    self.rconn.hset(unupdate_retry_queue, b_id + redis_sep + source + redis_sep + item['spider'], time_2_str())
                else:
                    db.sections.insert(sec_in_docs)
            else:
                return item
        except:
            log.msg(message=traceback.format_exc(), _level=log.ERROR)
        finally:
            if mongo:
                mongo.close()
