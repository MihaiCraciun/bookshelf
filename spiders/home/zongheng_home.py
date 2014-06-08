# encoding: utf-8
# Created on 2014-5-13
# @author: binge

from utils.conns_helper import RedisHelper
from utils.common import SpiderHelper, RedisStrHelper
from spiders.common_spider import CommonSpider
from collections import OrderedDict
from scrapy.http.request import Request
from scrapy.selector import Selector
import base64
import re
from utils.item_helper import ItemHelper

class ZHHomeSpider(CommonSpider):

    name = 'zhhome'

    def __init__(self, **kwargs):
        self.start_urls = ['http://www.zongheng.com']
        self.domain = 'http://www.zongheng.com'
        self.source_book_id_reg = '([0-9]+)'
        self.directory_pattern = 'http://book.zongheng.com/showchapter/%s.html'
        self.source_zh_name = u'纵横中文网'
        self.source_short_name = 'zh'

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
        desc = base64.encodestring(''.join(hxs.xpath('//div[@class="info_con"]/p//child::text()').extract()))
        yield ItemHelper.gene_book_desc_item(_id, desc)

        source_book_id = re.search(self.source_book_id_reg, url).group(1)
        directory_url = self.directory_pattern % source_book_id
        yield Request(directory_url, meta=response.meta, callback=self.directory_parse)

    def directory_parse(self, response):
        content = response._get_body()
        sec_nodes = re.findall('<td class="chapterBean" [^>]*>[^<]*(<a [^>]*>[^<]*</a>)', content)
        sec_nodes += re.findall('<td class="chapterBean" [^>]*>[^<]*<em class="vip">[^<]*</em>[^<]*(<a [^>]*>[^<]*</a>)', content)
        secs = OrderedDict()
        for sn in sec_nodes:
            url = re.search('.*href="([^"]+)".*', sn).group(1).strip()
            name = re.search('>([^<]+)<', sn).group(1).strip()
            secs[url] = name
#         
#         hxs = Selector(response)
#         try:
#             sec_nodes = hxs.xpath('//div[@id="chapterListPanel"]//td[@class="chapterBean"]')
#         except:
#             self.log('may be broken pipe, return.', level=log.ERROR)
#             yield None
#         secs = OrderedDict()
#         for sn in sec_nodes:
#             try:
#                 url = sn.xpath('a/@href').extract()[0]
#                 name = sn.xpath('@chapterName').extract()[0]
#                 secs[url] = name
#             except:
#                 self.log('may be broken pipe, continue.', level=log.ERROR)
#                 continue
        vs = RedisStrHelper.split(response.meta['info'])
        yield ItemHelper.gene_sections_item(self.source_short_name, self.source_zh_name, vs[0], vs[1], self.name, secs, 1)

