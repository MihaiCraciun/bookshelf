# encoding: utf-8
# Created on 2014-5-22
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from spiders.common_spider import CommonSpider
from scrapy.http.request import Request
from scrapy.selector import Selector
from collections import OrderedDict
from w3lib.url import urljoin_rfc
from utils.item_helper import ItemHelper

class RANWENHomeSpider(CommonSpider):

    name = 'lu5home'

    def __init__(self, **kwargs):
        self.start_urls = [kwargs['src']]
        self._id = kwargs['b_id']
        self.domain = 'http://www.ranwen.net'
        self.source_short_name = 'ranwen'
        self.source_zh_name = u'燃文小说'

    def parse(self, response):
        yield Request(Selector(response).xpath('//a[@id="m_reader"]/@href').extract()[0], callback=self.parse_dir)

    def parse_dir(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//div[@class="dccss"]/a')
        secs = OrderedDict()
        curr_url = response._get_url()
        for sn in sec_nodes:
            url = urljoin_rfc(curr_url, sn.xpath('@href').extract()[0])
            name = sn.xpath('child::text()').extract()[0]
            secs[url] = name
#         vs = RedisStrHelper.split(response.meta['info'])
#         yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)
        yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, self._id, self.start_urls[0], self.name, secs, 0)

