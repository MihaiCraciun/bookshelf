# encoding: utf-8
# Created on 2014-5-13
# @author: binge

import datetime
from scrapy import log
from spiders.common_spider import CommonSpider
from utils.item_helper import ItemHelper
from utils.common import TimeHelper, SpiderHelper
from utils.conns_helper import RedisHelper
from scrapy.selector import Selector
from scrapy.http.request import Request

class CSSpider(CommonSpider):

    name = 'cs'

    def __init__(self, **kwargs):
        self.start_urls = [
                           'http://chuangshi.qq.com/search/getSearchNovels.html?pageIndex=1&Website=&Subjectid=&Contentid=&Bookwords=all&Updatestatus=all&Lastupdate=all&Sortby=all&Isvip=all&TitlePinyin=all&TagList=all'
                           ]
        self.next_page_pattern = 'http://chuangshi.qq.com/search/getSearchNovels.html?pageIndex=%d&Website=&Subjectid=&Contentid=&Bookwords=all&Updatestatus=all&Lastupdate=all&Sortby=all&Isvip=all&TitlePinyin=all&TagList=all'
        self.source_name = u'创世中文网'
        self.domain = 'http://chuangshi.qq.com'
        self.home_spider = SpiderHelper.get_source_home_spider(self.name)
        self.curr_page_id = 1
        last_crawl_time_str = RedisHelper.get_last_crawl_time(self.name)
        if not last_crawl_time_str:
            self.last_crawl_time = TimeHelper.time_2_str(frt='%Y-%m-%d') + ' 00:00:00'
        else:
            self.last_crawl_time = last_crawl_time_str
        next_crawl_time = TimeHelper.time_2_str(delta= -SpiderHelper.get_every_crawl_timedelta_mins(), delta_unit='minutes')
        RedisHelper.set_next_crawl_time(self.name, next_crawl_time)
        self.year = str(datetime.datetime.now().year)
        self.source_short_name = 'cs'

    def parse(self, response):
        is_continue = True
        body = eval('u' + '"""' + response._get_body() + '"""').\
            replace('''"ListHTMl":"''', """"ListHTMl":'""").\
            replace('''<\/table>"}''', '''<\/table>'}''').\
            replace('''\r''', '''''').\
            replace('''\n''', '''''').\
            replace('\\', '')  # 1. change unicode to normal string, 2. format content.
        body_dict = eval(body)  # transfer body to a dict, contain two key: PageCount and ListHTMl.
        hxs = Selector(text=body_dict['ListHTMl'])
        book_nodes = hxs.xpath('//table/tr[position() > 1]')
        if not book_nodes:
            is_continue = False
        else:
            for bn in book_nodes:
                u_t = self.year[:2] + bn.xpath('td[last()]/span/child::text()').extract()[0].strip() + ":00"
                if u_t >= self.last_crawl_time:
                    n_c_nodes = bn.xpath('td[position() = 3]/a')  # book name
                    name = n_c_nodes[0].xpath('child::text()').extract()[0].strip()
                    source = self.domain + n_c_nodes[0].xpath('@href').extract()[0]
                    author = bn.xpath('td[last() - 1]/a/child::text()').extract()[0]

                    yield ItemHelper.gene_book_item(name, source, author, self.source_name, self.home_spider, self.source_short_name)
                else:
                    is_continue = False
                    break
        if is_continue:
            self.curr_page_id = self.curr_page_id + 1
            next_page = self.next_page_pattern % (self.curr_page_id)
            yield Request(next_page, callback=self.parse)
        else:
            self.log(message='%s spider sleep wait for next round.' % self.name, level=log.INFO)
            self.curr_page_id = 1
            self.last_crawl_time = RedisHelper.get_last_crawl_time(self.name)
            next_crawl_time = TimeHelper.time_2_str(delta= -SpiderHelper.get_every_crawl_timedelta_mins(), delta_unit='minutes')
            RedisHelper.set_next_crawl_time(self.name, next_crawl_time)
            SpiderHelper.source_spider_sleep()
            yield Request(self.start_urls[0], callback=self.parse)
