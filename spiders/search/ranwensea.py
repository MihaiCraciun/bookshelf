# encoding: utf-8
# Created on 2014-5-22
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from utils.common import SpiderHelper, SettingsHelper
from scrapy.http.request.form import FormRequest
from spiders.common_spider import CommonSpider
from scrapy.selector import Selector
from utils.item_helper import ItemHelper
import re

class RANWENSeaSpider(CommonSpider):

    name = 'ranwensea'

    def __init__(self, **kwargs):
        self.domain = 'http://www.ranwen.net'
        self.kw = kwargs['b_name']
        self.sea_url = 'http://www.ranwen.net/modules/article/search.php'
        self.b_id = kwargs['b_id']
        self.b_author = kwargs['b_author']
        self.lu5_home_pattern = 'http://www.lu5.com/book/[0-9]+.html'
        self.home_spider = SpiderHelper.get_sea_result_home_spider(self.name)

    def start_requests(self):
        return [FormRequest(url=self.sea_url, form_date={
                     'searchtype' : 'articlename',
                     'searchkey' : self.kw
                     }, callback=self.parse_result)]

    def parse_result(self, response):
        url = response._get_url()
        hxs = Selector(response)
        no_results = False
        if url == self.sea_url:
            book_nodes = hxs.xpath('//div[@id="searchhight"]//tr[position() > 1]/td[@class="odd"]')
            if book_nodes:
                for bn in book_nodes:
                    n_b_name_piecs = bn[0].xpath('a//child::text()').extract()
                    n_b_name = ''
                    for nbnp in n_b_name_piecs:
                        n_b_name = n_b_name + nbnp
                    if n_b_name == self.kw and str(bn[1].xpath('child::text()').extract()[0]).strip() == self.b_author:
                        n_home_url = bn[0].xpath('a/@href').extract()[0]
                        yield ItemHelper.gene_update_site_book_item(self.b_id, n_home_url, self.home_spider)
                        break
                else:
                    no_results = True
            else:
                no_results = True

        elif re.search(self.lu5_home_pattern, url):
            if hxs.xpath('//a[@class="green_12"]/b/child::text()').extract()[0] == self.kw:
                yield ItemHelper.gene_update_site_book_item(self.b_id, url, self.home_spider)
            else:
                no_results = True
        else:
            no_results = True
        if no_results:
            yield ItemHelper.gene_update_site_book_item(self.b_id, SettingsHelper.get_book_no_home_url_val(), self.home_spider)
