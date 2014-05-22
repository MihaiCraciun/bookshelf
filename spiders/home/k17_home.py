# encoding: utf-8
# Created on 2014-5-22
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from spiders.common_spider import CommonSpider
from scrapy.selector import Selector
import base64
from utils.item_helper import ItemHelper
from scrapy.http.request import Request
from collections import OrderedDict
import re

class K17HomeSpider(CommonSpider):

    name = 'k17home'

    def __init__(self, **kwargs):
        self.start_urls = [kwargs['src']]
        self._id = kwargs['b_id']
        self.domain = 'http://www.17k.com'
        self.directory_pattern = 'http://www.17k.com/list/%s.html'
        self.source_book_id_reg = 'book\/([0-9]+)\.html'
        self.source_zh_name = u'17K小说网'
        self.source_short_name = '17k'

    def parse(self, response):
        url = response._get_url()
        hxs = Selector(response)
        desc = base64.encodestring(hxs.xpath('//font[@itemprop="description"]/child::text()').extract()[0])
        yield ItemHelper.gene_book_desc_item(self._id, desc)

        source_book_id = re.search(self.source_book_id_reg, url).group(1)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, callback=self.directory_parse)

    def directory_parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//div[@class="directory_con"]/div[@class="con"]//li/a')
        secs = OrderedDict()
        for sn in sec_nodes:
            url = self.domain + sn.xpath('@href').extract()[0]
            name = sn.xpath('@tn').extract()[0]
            secs[url] = name
#         vs = RedisStrHelper.split(response.meta['info'])
#         yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)
        yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, self._id, self.start_urls[0], self.name, secs, 1)
