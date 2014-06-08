# encoding: utf-8
# Created on 2014-5-22
# @author: binge

from spiders.common_spider import CommonSpider
from scrapy.http.request.form import FormRequest
from scrapy.selector import Selector
import re
from utils.item_helper import ItemHelper
from utils.common import SpiderHelper, SettingsHelper

class LU5SeaSpider(CommonSpider):

    name = 'lu5sea'

    def __init__(self, **kwargs):
        self.domain = 'http://www.lu5.com'
        self.kw = kwargs['b_name']
        self.sea_url = 'http://www.lu5.com/modules/article/search.php'
        self.b_id = kwargs['b_id']
        self.b_author = kwargs['b_author']
        self.lu5_home_pattern = 'http://www.lu5.com/book/[0-9]+.html'
        self.home_spider = SpiderHelper.get_sea_result_home_spider(self.name)

    def start_requests(self):
        return [FormRequest(url=self.sea_url, formdata={
                     'searchtype' : 'articlename',
                     'searchkey' : self.kw
                     }, callback=self.parse_result)]

    def parse_result(self, response):
        url = response._get_url()
        hxs = Selector(response)
        no_results = False
        if url == self.sea_url:
            book_nodes = hxs.xpath('//dl[@id="content"]//tr[position() > 1]/td[@class="odd"]')
            if book_nodes and book_nodes[0].xpath('a/child::text()').extract()[0] == self.kw and str(book_nodes[1].xpath('child::text()').extract()[0]).strip() == self.b_author:
                n_home_url = book_nodes[0].xpath('a/@href').extract()[0]
                yield ItemHelper.gene_update_site_book_item(self.b_id, n_home_url, self.home_spider)
            else:
                no_results = True

        elif re.search(self.lu5_home_pattern, url) and str(hxs.xpath('//table[@id="at"]/tr[1]/td[2]/child::text()').extract()[0]).replace('&nbsp;', '').strip() == self.b_author:
            yield ItemHelper.gene_update_site_book_item(self.b_id, url, self.home_spider)
        else:
            no_results = True
        if no_results:
            yield ItemHelper.gene_update_site_book_item(self.b_id, SettingsHelper.get_book_no_home_url_val(), self.home_spider)
