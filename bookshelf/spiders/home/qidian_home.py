# encoding: utf-8
# Created on 2014-5-8
# @author: binge

import sys
import redis
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.spider import Spider
from bookshelf.settings import spider_redis_queues, redis_sep, redis_def_db,\
    redis_host, redis_port, crawling_key_prefix, crawling_key_expire
import time
from scrapy.http.request import Request
from scrapy.selector import Selector
import re
import base64
from bookshelf.items import BookDesc, Sections
from collections import OrderedDict


class QDHomeSpider(Spider):

    name = 'qdhome'

    def __init__(self, **kwargs):
        self.start_urls = ['http://www.qidian.com']
        self.directory_pattern = 'http://read.qidian.com/BookReader/%s.aspx'
        self.source_book_id_reg = '([0-9]+)'
        self.source_zh_name = u'起点中文网'
        self.source_short_name = 'qd'
        self.rconn = redis.Redis(host=redis_host, port=redis_port, db=redis_def_db)

    def parse(self, response):
        while 1:
            info = self.rconn.lpop(spider_redis_queues[self.name])
            if info:  # get a info from redis queue
                crawling_key = crawling_key_prefix + info
                if self.rconn.exists(crawling_key):
                    continue
                self.rconn.setex(crawling_key, '1', crawling_key_expire)
                home_url = info.split(redis_sep)[1]
                yield Request(home_url, meta = {'info' : info}, callback=self.home_parse)
                time.sleep(1)

    def home_parse(self, response):
        url = response._get_url()
        _id = response.meta['info'].split(redis_sep)[0]
        hxs = Selector(response)
        desc = base64.encodestring(hxs.xpath('//span[@itemprop="description"]/child').extract()[0])
        bc = BookDesc()
        bc['_id'] = _id
        bc['desc'] = desc
        yield bc

        source_book_id = re.search(self.source_book_id_reg, url)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, meta=response.meta, callback=self.directory_parse)

    def directory_parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//div[@id="bigcontbox"]//li/a')
        item = Sections()
        item['source_short_name'] = self.source_short_name
        item['source_zh_name'] = self.source_zh_name
        info = response.meta['info']
        item['b_id'] = info.split(redis_sep)[0]
        item['source'] = info.split(redis_sep)[1]
        item['spider'] = self.name
        secs = OrderedDict()
        for sn in sec_nodes:
            url = sn.xpath('@href').extract()[0]
            name = sn.xpath('child::text()').extract()[0]
            secs[url] = name
        yield item

    def __str__(self):
        return self.name




