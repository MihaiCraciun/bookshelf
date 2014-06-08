# encoding: utf-8
# Created on 2014-5-22
# @author: binge

from utils.conns_helper import RedisHelper
from utils.common import SpiderHelper, RedisStrHelper
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
        self.start_urls = ['http://www.17k.com']
        self.domain = 'http://www.17k.com'
        self.directory_pattern = 'http://www.17k.com/list/%s.html'
        self.source_book_id_reg = 'book\/([0-9]+)\.html'
        self.source_zh_name = u'17K小说网'
        self.source_short_name = '17k'
    
    def parse(self, response):
        while 1:
            try:
                info, home_url = RedisHelper.get_info_from_home_queue(self.name)
                if home_url:
                    yield Request(home_url, meta={'info' : info}, callback=self.home_parse)
            finally:
                SpiderHelper.sleep(1)
    
    def home_parse(self, response):
        url = response._get_url()
        _id = RedisStrHelper.split(response.meta['info'])[0]
        hxs = Selector(response)
        desc = base64.encodestring(''.join(hxs.xpath('//font[@itemprop="description"]//child::text()').extract()))
        yield ItemHelper.gene_book_desc_item(_id, desc)

        source_book_id = re.search(self.source_book_id_reg, url).group(1)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, meta=response.meta, callback=self.directory_parse)

    def directory_parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//div[@class="directory_con"]/div[@class="con"]//li/a')
        secs = OrderedDict()
        for sn in sec_nodes:
            url = self.domain + sn.xpath('@href').extract()[0]
            name = sn.xpath('@tn').extract()[0]
            secs[url] = name
        vs = RedisStrHelper.split(response.meta['info'])
        yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)
