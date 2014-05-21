# encoding: utf-8
# Created on 2014-5-21
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable


from scrapy.utils.project import get_project_settings
from scrapy.crawler import Crawler
from twisted.internet import reactor
from scrapy import log, signals
from scrapy.xlib.pydispatch import dispatcher

class SpiderCaller(object):

    def __init__(self):
        self.settings = get_project_settings()

    def run(self, spider_name, **spider_kwargs):
        self.spider_name = spider_name
        crawler = Crawler(self.settings)
        crawler.configure()
        spider = crawler.spiders.create(self.spider_name, **spider_kwargs)
        crawler.crawl(spider)
        crawler.start()
        log.start()
        log.msg('spider %s Running reactor...' % self.spider_name)
        ###
        dispatcher.connect(lambda : reactor.stop(), signal=signals.spider_closed)  # @UndefinedVariable
        reactor.run()  # @UndefinedVariable
        ###
        log.msg('spider %s Stop reactor...' % self.spider_name)

if __name__ == '__main__':
    SpiderCaller().run('qd')
