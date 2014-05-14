# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from bookshelf.utils.item_helper import sections_2_doc
from bookshelf.utils.conns_helper import get_redis_conn, get_mongo, close_mongo, \
    close_redis_conn, del_crawling_home
from bookshelf.utils.common import time_2_str
from scrapy.exceptions import DropItem
from bookshelf.items import Book, BookDesc, Sections
from bookshelf.settings import search_spider_queues, \
    redis_sep, spider_redis_queues, unupdate_retry_queue, ingrone_spiders, \
    user_favos_update_counts_key_prefix
import traceback
from scrapy import log
import datetime
# import md5
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class BookPipeline(object):
    '''
    exec book item.
    '''

    def process_item(self, item, spider):
        if not item.__class__ is Book:
            return item
        else:
            rconn = None
            mongo = None
            try:
                rconn = get_redis_conn()
                # conn mongodb
                mongo = get_mongo()
                db = mongo.bookshelf
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
                        if not sea in ingrone_spiders:
                            rconn.rpush(search_spider_queues[sea], _id + redis_sep + item['name'])
                else:  # this book has been crawled once or more.
                    book_homes = book['homes']
                    for sea in search_spider_queues:
                        if not sea in ingrone_spiders and (not sea in book_homes):  # if this book has some update sites not crawled yet, search it.
                            rconn.rpush(search_spider_queues[sea], _id + redis_sep + item['name'])
                        if sea in book_homes:  # get all home url to crawl.
                            home_url = book_homes[sea]
                            if home_url:
                                rconn.rpush(spider_redis_queues[sea], _id + redis_sep + home_url)

                # push current home link to its home spider queue, then the home spider will take the responsibility.
                rconn.rpush(spider_redis_queues[item['source_home_spider']], _id + redis_sep + source)
            except:
                log.msg(message=traceback.format_exc(), _level=log.ERROR)
            finally:
                close_mongo(mongo)
                close_redis_conn(rconn)

class BookDescPipeline(object):
    '''
    exec book description item.
    '''

    def process_item(self, item, spider):
        if not item.__class__ is BookDesc:
            return item
        else:
            mongo = None
            try:
                # conn mongodb
                mongo = get_mongo()
                db = mongo.bookshelf
                db.books.update({"_id" : item['_id']}, {'$set' : {"desc":item['desc']}})
            except:
                log.msg(message=traceback.format_exc(), _level=log.ERROR)
            finally:
                close_mongo(mongo)

class SectionsPipeline(object):
    '''
    exec sections item.
    '''

    def process_item(self, item, spider):
        if not item.__class__ is Sections:
            return item
        else:
            rconn = None
            mongo = None
            try:
                rconn = get_redis_conn()
                # conn mongodb
                mongo = get_mongo()
                db = mongo.bookshelf
                book = db.books.find_one({'_id' : item['b_id']})
                source = item['source']
                is_source = False
                if source == book['source']:
                    is_source = True
                b_id = item['b_id']
                source_short_name = item['source_short_name']
                sec_docs = db.sections.find({'b_id' : b_id, 'source_short_name' : source_short_name}, {'url' : 1})
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
                            sec_in_docs.append(sections_2_doc(b_id, source_short_name, item['source_zh_name'], sk, item['is_source'], sec_raws[sk], time_2_str(n + datetime.timedelta(seconds=i))))
                            i += 1
                        else:
                            break
                else:
                    for sr in sec_raws:
                        sec_in_docs.append(sections_2_doc(b_id, source_short_name, item['source_zh_name'], sr, item['is_source'], sec_raws[sr], time_2_str(n + datetime.timedelta(seconds=i))))
                        i += 1
                if not sec_in_docs and not is_source:  # current executing a update site, no doc to update, push info back to redis and retry.
                    rconn.hset(unupdate_retry_queue, b_id + redis_sep + source + redis_sep + item['spider'], time_2_str())
                else:
                    db.sections.insert(sec_in_docs)

                    user_favo_docs = db.user_favos.find({'b_ids' : b_id}, {'_id' : 1})
                    if user_favo_docs:  # push update count to users.
                        update_counts = len(sec_in_docs)
                        for ufd in user_favo_docs:
                            rconn.hincrby(user_favos_update_counts_key_prefix + ufd['_id'], b_id, update_counts)

                del_crawling_home(b_id + redis_sep + source)
            except:
                log.msg(message=traceback.format_exc(), _level=log.ERROR)
            finally:
                close_mongo(mongo)
                close_redis_conn(rconn)

class DropPipeline(object):
    '''
    if any item is transferred to this pipeline, drop it.
    '''

    def process_item(self, item, spider):
        if item:
            raise DropItem('this item(%s) is not instance of any Item.' % str(item))

