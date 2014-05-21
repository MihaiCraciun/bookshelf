# encoding: utf-8
# Created on 2014-5-14
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.spider import Spider
from scrapy.http.request import Request
from utils.item_helper import ItemHelper
from scrapy.selector import Selector
import base64
import re
from collections import OrderedDict

class CSHomeSpider(Spider):

    name = 'cshome'

    def __init__(self, **kwargs):
#         self.start_urls = ['http://chuangshi.qq.com']
        self.start_urls = [kwargs['src']]
        self._id = kwargs['b_id']
        self.domain = 'http://chuangshi.qq.com'
        self.directory_pattern = 'http://chuangshi.qq.com/read/bk/js/%s-m.html'
        self.source_book_id_reg = '([0-9]+)\-1'
        self.source_zh_name = u'创世中文网'
        self.source_short_name = 'cs'

#     def parse(self, response):
#         while 1:
#             try:
#                 info, home_url = RedisHelper.get_info_from_home_queue(spider_name=self.name)
#                 if home_url:
#                     yield Request(home_url, meta={'info' : info}, callback=self.home_parse)
#             finally:
#                 SpiderHelper.sleep(1)
#
#     def home_parse(self, response):
#         url = response._get_url()
#         _id = RedisStrHelper.split(response.meta['info'])[0]
#         hxs = Selector(response)
#         desc = base64.encodestring(hxs.xpath('//div[@class="info"]/p/child::text()').extract()[0])
#         yield ItemHelper.gene_book_desc_item(_id, desc)
#
#         source_book_id = re.search(self.source_book_id_reg, url).group(1)
#         directory_url = self.directory_pattern % source_book_id
#         yield Request(directory_url, meta=response.meta, callback=self.directory_parse)

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, headers={'Referer' : self.domain})

    def parse(self, response):
        url = response._get_url()
        hxs = Selector(response)
        desc = base64.encodestring(hxs.xpath('//div[@class="info"]/p/child::text()').extract()[0])
        yield ItemHelper.gene_book_desc_item(self._id, desc)

        source_book_id = re.search(self.source_book_id_reg, url).group(1)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, callback=self.directory_parse)

    def directory_parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//ul[@class="block_ul"]/li/a')
        secs = OrderedDict()
        for sn in sec_nodes:
            url = self.domain + sn.xpath('@href').extract()[0]
            name = sn.xpath('b/child::text()').extract()[0]
            secs[url] = name
#         vs = RedisStrHelper.split(response.meta['info'])
#         yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)
        yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, self._id, self.start_urls[0], self.name, secs, 1)

    def __str__(self):
        return self.name
