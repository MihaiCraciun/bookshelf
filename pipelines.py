# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from utils.item_helper import ItemHelper
from utils.conns_helper import MongoHelper, RedisHelper
from utils.common import TimeHelper, RedisStrHelper, SettingsHelper
from scrapy.exceptions import DropItem
from items import Book, BookDesc, Sections, UpdateSiteBook
from settings import sea_ingrone_spiders, user_favos_update_counts_key_prefix, \
    spider_redis_queues, book_no_home_url_val,\
    search_spider_names, \
    update_site_spider_info_queue, search_spider_info_queue,\
    monitor_main_spider_queue
import traceback
from scrapy import log, signals
import datetime
from scrapy.xlib.pydispatch import dispatcher
# import md5
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class BookPipeline(object):
    '''
    exec book item.
    '''

    def __init__(self):
#         dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        RedisHelper.get_redis_conn().srem(monitor_main_spider_queue, spider.name)

    def process_item(self, item, spider):
        if not item.__class__ is Book:
            return item
        else:
            rconn = None
            mongo = None
            try:
                rconn = RedisHelper.get_redis_conn()
                # conn mongodb
                mongo = MongoHelper.get_mongo()
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
                    b['source_short_name'] = item['source_short_name']
                    b['update_time']  = TimeHelper.time_2_str()
                    db.books.insert(b)  # insert it to mongodb

                    ##########################################################
                    # this book must be searched in other update sites.
                    for sea in search_spider_names:
                        if not sea in sea_ingrone_spiders:
                            rconn.sadd(search_spider_info_queue, {'spider_name' : search_spider_names[sea], 'b_id' : _id, 'b_name' : item['name'], 'b_author' : item['author']})
                    # push current home link to its home spider queue, then the home spider will take the responsibility.
                    rconn.rpush(spider_redis_queues[item['source_home_spider']], RedisStrHelper.contact(_id, source))
                    ##########################################################

                else:  # this book has been crawled once or more.
                    book_homes = book['homes']
                    ###########################################################
                    for home_spider_name in search_spider_names:
                        if not home_spider_name in sea_ingrone_spiders and (not home_spider_name in book_homes):  # if this book has some update sites not crawled yet, search it.
                            rconn.sadd(search_spider_info_queue, {'spider_name' : search_spider_names[home_spider_name], 'b_id' : _id, 'b_name' : item['name'], 'b_author' : item['author']})
                            continue
                        if home_spider_name in book_homes:  # get all home url to crawl.
                            home_url = book_homes[home_spider_name]
                            if home_url and not home_url == book_no_home_url_val:
                                if not home_spider_name in sea_ingrone_spiders:
                                    rconn.sadd(update_site_spider_info_queue, {'spider_name' : home_spider_name, 'b_id' : _id, 'src' : home_url})
                                else:
                                    rconn.rpush(spider_redis_queues[home_spider_name], RedisStrHelper.contact(_id, home_url))

                    ###########################################################

            except:
                log.msg(message=traceback.format_exc(), _level=log.ERROR)
            finally:
                MongoHelper.close_mongo(mongo)
                RedisHelper.close_redis_conn(rconn)

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
                mongo = MongoHelper.get_mongo()
                db = mongo.bookshelf
                db.books.update({"_id" : item['_id']}, {'$set' : {"desc":item['desc']}})
            except:
                log.msg(message=traceback.format_exc(), _level=log.ERROR)
            finally:
                MongoHelper.close_mongo(mongo)

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
                rconn = RedisHelper.get_redis_conn()
                # conn mongodb
                mongo = MongoHelper.get_mongo()
                db = mongo.bookshelf
                is_source = item['is_source']
                b_id = item['b_id']
                source_short_name = item['source_short_name']
                sec_docs = db.sections.find({'b_id' : b_id, 'source_short_name' : source_short_name}, {'url' : 1})
                sec_raws = item['secs']
                sec_in_docs = []
                n = datetime.datetime.now()
                i = 0
                sr_ks = sec_raws.keys()[::-1]
                if sec_docs:
                    old_urls = set()
                    for sd in sec_docs:
                        old_urls.add(sd['url'])
                    for sk in sr_ks:
                        if not sk in old_urls:
                            sec_in_docs.append(ItemHelper.sections_2_doc(b_id, source_short_name, item['source_zh_name'], sk, is_source,
                                                                         sec_raws[sk], TimeHelper.time_2_str(n - datetime.timedelta(seconds=i))))
                            i += 1
                        else:
                            break
                else:
                    for sk in sr_ks:
                        sec_in_docs.append(ItemHelper.sections_2_doc(b_id, source_short_name, item['source_zh_name'], sk, is_source,
                                                                     sec_raws[sk], TimeHelper.time_2_str(n - datetime.timedelta(seconds=i))))
                        i += 1
                if not sec_in_docs:
                    pass
#                     if not is_source:  # current executing a update site, no doc to update, push info back to redis and retry.
#                         rconn.hset(unupdate_retry_queue, RedisStrHelper.contact(b_id, source, item['spider']), TimeHelper.time_2_str())
                else:
                    db.sections.insert(sec_in_docs)
                    db.books.update({'_id' : b_id}, {'$set' : {"update_time" : TimeHelper.time_2_str(), "newest_sec" : sec_in_docs[0]['name']}})
                    if is_source:
                        user_favo_docs = db.user_favos.find({'b_ids' : b_id}, {'_id' : 1})
                        if user_favo_docs:  # push update count to users.
                            update_counts = len(sec_in_docs)
                            for ufd in user_favo_docs:
                                rconn.hincrby(user_favos_update_counts_key_prefix + ufd['_id'], b_id, update_counts)

#                 RedisHelper.del_crawling_home(RedisStrHelper.contact(b_id, source))
            except:
                log.msg(message=traceback.format_exc(), _level=log.ERROR)
            finally:
                MongoHelper.close_mongo(mongo)
                RedisHelper.close_redis_conn(rconn)

class UpdateSiteBookPipeline(object):

    def process_item(self, item, spider):
        if not item.__class__ is UpdateSiteBook:
            return item
        else:
            mongo = None
            rconn = None
            try:
                rconn = RedisHelper.get_redis_conn()
                # conn mongodb
                mongo = MongoHelper.get_mongo()
                db = mongo.bookshelf
                home_spider_name = item['home_spider']
                _id = item['_id']
                home_url = item['home_url']
                db.books.update({"_id" : _id}, {'$set' : {"homes." + home_spider_name : home_url}})
                if not home_url == SettingsHelper.get_book_no_home_url_val():
                    rconn.add(update_site_spider_info_queue, {'spider_name' : home_spider_name, 'b_id' : _id, 'src' : home_url})
            except:
                log.msg(message=traceback.format_exc(), _level=log.ERROR)
            finally:
                MongoHelper.close_mongo(mongo)
                RedisHelper.close_redis_conn(rconn)

class DropPipeline(object):
    '''
    if any item is transferred to this pipeline, drop it.
    '''

    def process_item(self, item, spider):
        if item:
            raise DropItem('this item(%s) is not instance of any Item.' % str(item))

