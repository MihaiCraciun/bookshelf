# encoding: utf-8
# Created on 2014-5-22
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.selector import Selector
from scrapy import log
from utils.item_helper import ItemHelper
from scrapy.http.request import Request
import datetime
from utils.common import SpiderHelper, TimeHelper
from utils.conns_helper import RedisHelper
from spiders.common_spider import CommonSpider

class K17Spiser(CommonSpider):

    name = 'k17'

    def __init__(self, **kwargs):
        self.start_urls = [
                           'http://all.17k.com/all'
                           ]
        self.source_name = u'17K小说网'
        self.domain = 'http://www.17k.com'
        self.next_page_domain = 'http://all.17k.com'
        self.home_spider = SpiderHelper.get_source_home_spider(self.name)
        last_crawl_time_str = RedisHelper.get_last_crawl_time(self.name)
        if not last_crawl_time_str:
            self.last_crawl_time = TimeHelper.time_2_str(frt='%Y-%m-%d') + ' 00:00:00'
        else:
            self.last_crawl_time = last_crawl_time_str
        next_crawl_time = TimeHelper.time_2_str(delta= -SpiderHelper.get_every_crawl_timedelta_mins(), delta_unit='minutes')
        RedisHelper.set_next_crawl_time(self.name, next_crawl_time)

    def parse(self, response):
        is_continue = True
        hxs = Selector(response)
        book_nodes = hxs.xpath('//div[@class="alltable"]//tr[positions() > 2]')
        if not book_nodes:
            self.log(message='%s spider get nothing in home page, current url is %s' % (self.name, response._get_url()), level=log.WARNING)
            is_continue = False
        else:
            for bn in book_nodes:
                u_time = bn.xpath('td[@class="td7"]/child::text()').extract()[0] + ":00"
                if u_time >= self.last_crawl_time:
                    source = bn.xpath('td[@class="td3"]//a/@href').extract()[0]  # first link
                    name = bn.xpath('td[@class="td3"]//a/child::text()').extract()[0]  # book name
                    author = bn.xpath('td[@class="td6"]/a/child::text()').extract()[0]

                    yield ItemHelper.gene_book_item(name, source, author, self.source_name, self.home_spider)
                else:
                    is_continue = False  # if the section publish time is less than last crawl time, can't continue.
                    break
        if is_continue:
            next_page_nodes = hxs.xpath('//a[@class="on"]/following-sibling::a')
            if next_page_nodes:
                next_page = self.next_page_domain + next_page_nodes[0].xpath('@href').extract()[0]
                yield Request(next_page, callback=self.parse)
            else:
                self.log(message='%s spider cannot get next page, current url is %s' % (self.name, response._get_url()), level=log.WARNING)
        else:
            self.log(message='%s spider sleep wait for next round.' % self.name, level=log.INFO)
            self.last_crawl_time = RedisHelper.get_last_crawl_time(self.name)
            next_crawl_time = self.gene_next_crawl_time(datetime.datetime.now() - datetime.timedelta(minutes=SpiderHelper.get_every_crawl_timedelta_mins()))
            RedisHelper.set_next_crawl_time(self.name, next_crawl_time)
#             SpiderHelper.source_spider_sleep()
#             yield Request(self.start_urls[0], callback=self.parse)
