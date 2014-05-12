# encoding: utf-8
# Created on 2014-5-7
# @author: binge

import sys
from scrapy import log
from bookshelf.utils import get_last_crawl_time, set_next_crawl_time
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from bookshelf.items import Book
import datetime
from bookshelf.settings import qd_home_spider, \
    source_spider_sleep, every_crawl_timedelta_mins

from scrapy.http.request import Request
import time

from scrapy.spider import Spider
from scrapy.selector import Selector

class QDSpider(Spider):

    name = 'qd'

    def __init__(self, **kwargs):
        self.start_urls = ['http://all.qidian.com/Book/BookStore.aspx?ChannelId=-1&SubCategoryId=-1&Tag=all&Size=-1&Action=-1&OrderId=6&P=all&PageIndex=1&update=4']
        self.source_name = u'起点中文网'
        self.domain = 'http://www.qidian.com'
        now = datetime.datetime.now()
        self.year = str(now.year)
        self.month = str(now.month)
        self.day = str(now.day)

        last_crawl_time_str = get_last_crawl_time(self.name)
        if not last_crawl_time_str:
            self.last_crawl_time = '%s-%s-%s 00:00:00' % (self.year, self.month, self.day)
        else:
            self.last_crawl_time = last_crawl_time_str
        self.gene_next_crawl_time = lambda (t) : (str(t.year) + '-' + str(t.month) + '-' + str(t.day) + ' ' + t.strftime('%X'))
        next_crawl_time = self.gene_next_crawl_time(now - datetime.timedelta(minutes=every_crawl_timedelta_mins))
#         next_crawl_time = time_2_str(now - datetime.timedelta(minutes=every_crawl_timedelta_mins))
        set_next_crawl_time(self.name, next_crawl_time)

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, headers={'Referer' : self.domain})

    def parse(self, response):
        is_continue = True
        hxs = Selector(response)
        book_nodes = hxs.xpath('//div[@class="sw1"] | //div[@class="sw2"]')
        for bn in book_nodes:
            u_time = self.year[:2] + bn.xpath('div[@class="swe"]/child::text()').extract()[0] + ":00"
            if u_time >= self.last_crawl_time:
                source = self.domain + bn.xpath('div[@class="swb"]/span[@class="swbt"]/a/@href').extract()[0]  # first link

                name = bn.xpath('div[@class="swb"]/span[@class="swbt"]/a/child::text()').extract()[0]  # book name
                author = bn.xpath('div[@class="swd"]/a/child::text()').extract()[0]
                item = Book()
                item['name'] = name
                item['source'] = source
                item['source_name'] = self.source_name
                item['author'] = author
                item['homes'] = {qd_home_spider : source}
                item['source_spider'] = qd_home_spider

                yield item
            else:
                is_continue = False  # if the section publish time is less than last crawl time, can't continue.
                break
        if is_continue:
            next_page_nodes = hxs.xpath('//div[@class="storelistbottom"]/a[@class="f_s"]/following-sibling::a')
            if next_page_nodes:
                next_page = next_page_nodes[0].xpath('@href').extract()[0]
                yield Request(next_page, callback=self.parse)
        else:
            self.log(message = 'spider sleep wait for next round.', level = log.INFO)
#             next_crawl_time = time_2_str(time = datetime.datetime.now() - datetime.timedelta(minutes=every_crawl_timedelta_mins))
            next_crawl_time = self.gene_next_crawl_time(datetime.datetime.now() - datetime.timedelta(minutes=every_crawl_timedelta_mins))
            set_next_crawl_time(self.name, next_crawl_time)
            time.sleep(source_spider_sleep)
            yield Request(self.start_urls[0], callback=self.parse)

    def __str__(self):
        return self.name
