# encoding: utf-8
# Created on 2014-5-13
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from bookshelf.utils.item_helper import gene_book_item
from scrapy.selector import Selector
from scrapy.spider import Spider
from bookshelf.utils.common import get_source_home_spider, time_2_str,\
    get_every_crawl_timedelta_mins
from bookshelf.utils.conns_helper import get_last_crawl_time,\
    set_next_crawl_time
from scrapy.http.request import Request

class CSSpider(Spider):

    name = 'cs'

    def __init__(self, **kwargs):
        self.start_urls = [
                           'http://chuangshi.qq.com/read/ajax/Novels.html?pageIndex=1&Website=&Subjectid=&Contentid=&Bookwords=all&Updatestatus=all&Lastupdate=all&Sortby=all&Isvip=all&TitlePinyin=all&TagList=all'
                           ]
        self.next_page_pattern = 'http://chuangshi.qq.com/read/ajax/Novels.html?pageIndex=%d&Website=&Subjectid=&Contentid=&Bookwords=all&Updatestatus=all&Lastupdate=all&Sortby=all&Isvip=all&TitlePinyin=all&TagList=all'
        self.source_name = u'创世书库'
        self.domain = 'http://chuangshi.qq.com'
        self.home_spider = get_source_home_spider[self.name]
        self.curr_page_id = 1
        last_crawl_time_str = get_last_crawl_time(self.name)
        if not last_crawl_time_str:
            self.last_crawl_time = time_2_str(frt='%Y-%m-%d') + ' 00:00:00'
        else:
            self.last_crawl_time = last_crawl_time_str
        next_crawl_time = time_2_str(delta=-get_every_crawl_timedelta_mins(), delta_unit='minutes')
        set_next_crawl_time(self.name, next_crawl_time)

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, headers={'Referer' : self.domain})

    def parse(self, response):
        is_continue = True
        body = eval('u' + '"""' + response._get_body() + '"""').\
            replace('''"ListHTMl":"''', """"ListHTMl":'""").\
            replace('''<\/div>"}''', '''<\/div>'}''').\
            replace('\\', '') # 1. change unicode to normal string, 2. format content.
        body_dict = eval(body) # transfer body to a dict, contain too key: PageCount and ListHTMl.
        hxs = Selector(text = body_dict['ListHTMl'])
        book_nodes = hxs.xpath('//table/tr[position() > 1]')
        if not book_nodes:
            is_continue = False
        else:





            for bn in book_nodes:
                u_t = bn.xpath('span[@class="time"]/@title').extract()[0]
                if u_t >= self.last_crawl_time:
                    n_c_nodes = bn.xpath('span[@class="chap"]/a') # book name and section nodes
                    name = n_c_nodes[0].xpath('@title').extract()[0]
                    source = n_c_nodes[0].xpath('@href').extract()[0]
                    author = bn.xpath('span[@class="author"]/a/@title').extract()[0]

                    yield gene_book_item(name, source, author, self.source_name, self.home_spider)
                else:
                    is_continue = False
                    break
        if is_continue:
            pass
        else:
            pass
