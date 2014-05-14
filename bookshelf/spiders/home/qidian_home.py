# encoding: utf-8
# Created on 2014-5-8
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from bookshelf.utils.conns_helper import RedisHelper
from bookshelf.utils.common import SpiderHelper, RedisStrHelper
from bookshelf.utils.item_helper import ItemHelper
from scrapy.spider import Spider
from scrapy.http.request import Request
from scrapy.selector import Selector
import re
import base64
from collections import OrderedDict


class QDHomeSpider(Spider):

    name = 'qdhome'

    def __init__(self, **kwargs):
        self.start_urls = ['http://www.qidian.com']
        self.directory_pattern = 'http://read.qidian.com/BookReader/%s.aspx'
        self.source_book_id_reg = '([0-9]+)'
        self.source_zh_name = u'起点中文网'
        self.source_short_name = 'qd'

    def parse(self, response):
        while 1:
            try:
                info, home_url = RedisHelper.get_info_from_home_queue(spider_name=self.name)
                if home_url:
                    yield Request(home_url, meta={'info' : info}, callback=self.home_parse)
            finally:
                SpiderHelper.sleep(1)

    def home_parse(self, response):
        url = response._get_url()
        _id = RedisStrHelper.split(response.meta['info'])[0]
        hxs = Selector(response)
        desc = base64.encodestring(hxs.xpath('//span[@itemprop="description"]/child::text()').extract()[0])
        yield ItemHelper.gene_book_desc_item(_id, desc)

        source_book_id = re.search(self.source_book_id_reg, url).group(1)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, meta=response.meta, callback=self.directory_parse)

    def directory_parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//div[@id="bigcontbox"]//li/a')
        secs = OrderedDict()
        for sn in sec_nodes:
            url = sn.xpath('@href').extract()[0]
            name = sn.xpath('child::text()').extract()[0]
            secs[url] = name
        vs = RedisStrHelper.split(response.meta['info'])
        yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)

    def __str__(self):
        return self.name




