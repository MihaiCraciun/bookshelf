# encoding: utf-8
# Created on 2014-5-12
# @author: binge

import sys
from scrapy.http.response.text import TextResponse
import traceback
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from spiders.common_spider import CommonSpider
from utils.conns_helper import RedisHelper
from utils.common import TimeHelper, SpiderHelper
from utils.item_helper import ItemHelper
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy import log
import re

class ZHSpier(CommonSpider):
    name = 'zh'

    def __init__(self, **kwargs):
        self.start_urls = [
                           'http://book.zongheng.com/store/c0/c0/b0/u0/p1/v9/s9/t0/ALL.html'
                           ]
        self.next_page_pattern = 'http://book.zongheng.com/store/c0/c0/b0/u0/p%d/v9/s9/t0/ALL.html'
        self.source_name = u'纵横中文网'
        self.domain = 'http://www.zongheng.com'
        self.home_spider = SpiderHelper.get_source_home_spider(self.name)
        last_crawl_time_str = RedisHelper.get_last_crawl_time(self.name)
        if not last_crawl_time_str:
            self.last_crawl_time = TimeHelper.time_2_str(frt='%Y-%m-%d') + ' 00:00:00'
        else:
            self.last_crawl_time = last_crawl_time_str
        next_crawl_time = TimeHelper.time_2_str(delta= -SpiderHelper.get_every_crawl_timedelta_mins(), delta_unit='minutes')
        RedisHelper.set_next_crawl_time(self.name, next_crawl_time)
        self.source_short_name = 'zh'

    def parse(self, response):
        is_continue = True
        hxs = Selector(response)
        book_nodes = hxs.xpath('//ul[@class="main_con"]/li')
        if not book_nodes:
            is_continue = False
        else:
            for bn in book_nodes:
                try:
                    u_t = bn.xpath('span[@class="time"]/@title').extract()[0]
                except:
                    self.log('may be broken pipe, continue.', level=log.ERROR)
                    continue
                if u_t >= self.last_crawl_time:
                    n_c_nodes = bn.xpath('span[@class="chap"]/a')  # book name
                    name = n_c_nodes[0].xpath('@title').extract()[0]
                    source = n_c_nodes[0].xpath('@href').extract()[0]
                    author = bn.xpath('span[@class="author"]/a/@title').extract()[0]

                    yield ItemHelper.gene_book_item(name, source, author, self.source_name, self.home_spider, self.source_short_name)
                else:
                    is_continue = False
                    break
        if is_continue:
            curr_url = response._get_url()
            reg = '.*/u0/p([0-9]+)/v9.*'
            page_id = re.search(pattern=reg, string=curr_url).group(1)
            next_page = self.next_page_pattern % (int(page_id) + 1)

            yield Request(next_page, callback=self.parse)
        else:
            self.log(message='%s spider sleep wait for next round.' % self.name, level=log.INFO)
            self.last_crawl_time = RedisHelper.get_last_crawl_time(self.name)
            next_crawl_time = TimeHelper.time_2_str(delta= -SpiderHelper.get_every_crawl_timedelta_mins(), delta_unit='minutes')
            RedisHelper.set_next_crawl_time(self.name, next_crawl_time)
            SpiderHelper.source_spider_sleep()
            yield Request(self.start_urls[0], callback=self.parse)

