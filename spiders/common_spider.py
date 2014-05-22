# encoding: utf-8
# Created on 2014-5-22
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.spider import Spider
from scrapy.http.request import Request

class CommonSpider(Spider):

    def make_requests_from_url(self, url):
        headers = None
        if hasattr(self, 'domain'):
            headers = {'Referer' : self.domain}
        return Request(url, dont_filter=True, headers=headers)

    def __str__(self):
        return self.name
