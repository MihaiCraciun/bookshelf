# encoding: utf-8
# Created on 2014-5-23
# @author: binge

from scrapy.selector import Selector
from collections import OrderedDict
from utils.item_helper import ItemHelper
from spiders.common_spider import CommonSpider

class FQXSWHomeSpider(CommonSpider):

    name = 'fqxswhome'

    def __init__(self, **kwargs):
        self.start_urls = [kwargs['src']]
        self._id = kwargs['b_id']
        self.domain = 'http://www.fqxsw.com'
        self.source_short_name = 'fqxsw'
        self.source_zh_name = u'番茄小说网'

    def parse(self, response):
        hxs = Selector(response)
        sec_nodes = hxs.xpath('//div[@class="booklist clearfix"]/li/span/a')
        secs = OrderedDict()
        for sn in sec_nodes:
            url = self.domain + sn.xpath('@href').extract()[0]
            name = sn.xpath('child::text()').extract()[0]
            secs[url] = name
#         vs = RedisStrHelper.split(response.meta['info'])
#         yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)
        yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, self._id, self.start_urls[0], self.name, secs, 0)

