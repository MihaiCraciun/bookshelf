# encoding: utf-8
# Created on 2014-5-8
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.spider import Spider
from bookshelf.settings import spider_redis_queues, redis_sep
import time
from scrapy.http.request import Request
from scrapy.selector import Selector
import re
import base64
from bookshelf.items import BookDesc, Sections
from collections import OrderedDict


class QDHomeSpider(Spider):

    name = 'qdhome'

    def __init__(self, i):
        self.start_urls = ['http://www.qidian.com']
        self.directory_pattern = 'http://read.qidian.com/BookReader/%s.aspx'
        self.source_book_id_reg = '([0-9]+)'
        self.source_zh_name = u'起点中文网'
        self.source_short_name = 'qd'

    def parse(self, response):
        while 1:
            info = self.rconn.lpop(spider_redis_queues[self.name])
            if info:  # get a info from redis queue
                _id = info.split(redis_sep)[0]
                home_url = info.split(redis_sep)[1]
                yield Request(home_url, meta = {'_id' : _id, 'url' : home_url}, callback=self.home_parse)
                break
            else:
                time.sleep(1)

    def home_parse(self, response):
        url = response.meta['url']
        _id = response.meta['_id']
        hxs = Selector(response)
        desc = base64.encodestring(hxs.xpath('//span[@itemprop="description"]/child').extract()[0])
        bc = BookDesc()
        bc['_id'] = _id
        bc['desc'] = desc
        yield bc

        source_book_id = re.search(self.source_book_id_reg, url)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, meta={'_id' : _id, 'source' : url}, callback=self.directory_parse)

    def directory_parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//div[@id="bigcontbox"]//li/a')
        item = Sections()
        item['source_short_name'] = self.source_short_name
        item['source_zh_name'] = self.source_zh_name
        item['b_id'] = response.meta['_id']
        item['source'] = response.meta['source']
        item['spider'] = self.name
        secs = OrderedDict()
        for sn in sec_nodes:
            url = sn.xpath('@href').extract()[0]
            name = sn.xpath('child::text()').extract()[0]
            secs[url] = name
        yield item





