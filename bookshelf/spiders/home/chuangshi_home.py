# encoding: utf-8
# Created on 2014-5-14
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.spider import Spider
from bookshelf.utils.conns_helper import get_info_from_home_queue
from scrapy.http.request import Request
from bookshelf.utils.common import sleep, split_redis_str
from cssselect.parser import Selector
import base64
from bookshelf.utils.item_helper import gene_book_desc_item, gene_sections_item
import re
from collections import OrderedDict

class CSHomeSpider(Spider):

    name = 'cshome'

    def __init__(self, **kwargs):
        self.start_urls = ['http://chuangshi.qq.com']
        self.domain = 'http://chuangshi.qq.com'
        self.directory_pattern = 'http://chuangshi.qq.com/read/bk/js/%s-m.html'
        self.source_book_id_reg = '([0-9]+)\-1'
        self.source_zh_name = u'创世中文网'
        self.source_short_name = 'cs'

    def parse(self, response):
        while 1:
            try:
                info, home_url = get_info_from_home_queue(spider_name=self.name)
                if home_url:
                    yield Request(home_url, meta={'info' : info}, callback=self.home_parse)
            finally:
                sleep(1)

    def home_parse(self, response):
        url = response._get_url()
        _id = split_redis_str(response.meta['info'])[0]
        hxs = Selector(response)
        desc = base64.encodestring(hxs.xpath('//div[@class="info"]/p/child::text()').extract()[0])
        yield gene_book_desc_item(_id, desc)

        source_book_id = re.search(self.source_book_id_reg, url).group(1)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, meta=response.meta, callback=self.directory_parse)

    def directory_parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//ul[@class="block_ul"]/li/a')
        secs = OrderedDict()
        for sn in sec_nodes:
            url = self.domain + sn.xpath('@href').extract()[0]
            name = sn.xpath('b/child::text()').extract()[0]
            secs[url] = name
        vs = split_redis_str(response.meta['info'])
        yield gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)

    def __str__(self):
        return self.name
