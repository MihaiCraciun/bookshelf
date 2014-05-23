# encoding: utf-8
# Created on 2014-5-22
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from spiders.common_spider import CommonSpider
from utils.common import SpiderHelper, SettingsHelper
from utils.item_helper import ItemHelper
from scrapy.http.request.form import FormRequest
from scrapy.selector import Selector

class BXWXSeaSpider(CommonSpider):

    name = 'bxwxsea'

    def __init__(self, **kwargs):
        self.domain = 'http://www.bxwx.org'
        self.kw = kwargs['b_name']
        self.sea_url = 'http://www.bxwx.org/modules/article/searchcc.php'
        self.b_id = kwargs['b_id']
        self.b_author = kwargs['b_author']
        self.home_spider = SpiderHelper.get_sea_result_home_spider(self.name)

    def start_requests(self):
        return [FormRequest(url=self.sea_url, form_date={
                     'searchtype' : 'articlename',
                     'searchkey' : self.kw
                     }, callback=self.parse_result)]

    def parse_result(self, response):
        hxs = Selector(response)
        book_nodes = hxs.xpath('//div[@id="centerm"]//tr[position() > 1]/td[@class="odd"]')
        if book_nodes and book_nodes[0].xpath('a/child::text()').extract()[0] == self.kw and str(book_nodes[1].xpath('child::text()').extract()[0]).strip() == self.b_author:
            n_home_url = self.domain + book_nodes[0].xpath('a/@href').extract()[0]
            yield ItemHelper.gene_update_site_book_item(self.b_id, n_home_url, self.home_spider)
        else:
            no_results = True
        if no_results:
            yield ItemHelper.gene_update_site_book_item(self.b_id, SettingsHelper.get_book_no_home_url_val(), self.home_spider)
