# encoding: utf-8
# Created on 2014-5-23
# @author: binge

import re
from spiders.common_spider import CommonSpider
from utils.common import SpiderHelper, SettingsHelper
from scrapy.http.request.form import FormRequest
from cssselect.parser import Selector
from utils.item_helper import ItemHelper

class FQXSWSeaSpider(CommonSpider):

    name = 'fqxswsea'

    def __init__(self, **kwargs):
        self.domain = 'http://www.fqxsw.com'
        self.kw = kwargs['b_name']
        self.sea_url = 'http://www.fqxsw.com/modules/article/search.php'
        self.b_id = kwargs['b_id']
        self.b_author = kwargs['b_author']
        self.fqxsw_home_pattern = 'http://www.fqxsw.com/book/[0-9a-zA-Z]+/'
        self.home_spider = SpiderHelper.get_sea_result_home_spider(self.name)

    def start_requests(self):
        return [FormRequest(url=self.sea_url, formdata={
                     'searchkey' : self.kw
                     }, callback=self.parse_result)]

    def parse_result(self, response):
        url = response._get_url()
        hxs = Selector(response)
        no_results = False
        if url == self.sea_url:
            book_nodes = hxs.xpath('//ul[@class="articlelist"]/li[[position() > 1]')
            if book_nodes:
                for bn in book_nodes:
                    if bn.xpath('div[@class="c2"]/a/child::text()').extract()[0] == self.b_author and self.kw == bn.xpath('div[@class="c1"]/a/child::text()').extract()[0]:
                        n_home_url = self.domain + bn.xpath('div[@class="c1"]/a/@href').extract()[0]
                        yield ItemHelper.gene_update_site_book_item(self.b_id, n_home_url, self.home_spider)
                        break
                else:
                    no_results = True
            else:
                no_results = True

        elif re.search(self.fqxsw_home_pattern, url) and re.search('^作者：(.+)  分类：.+$', str(hxs.xpath('//span[@class="author"]/child::text()').extract()[0])).group(1).strip() == self.b_author:
            yield ItemHelper.gene_update_site_book_item(self.b_id, url, self.home_spider)
        else:
            no_results = True
        if no_results:
            yield ItemHelper.gene_update_site_book_item(self.b_id, SettingsHelper.get_book_no_home_url_val(), self.home_spider)
