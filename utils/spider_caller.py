# encoding: utf-8
# Created on 2014-5-21
# @author: binge

from scrapy.utils.project import get_project_settings
from scrapy.crawler import Crawler
from twisted.internet import reactor
from scrapy import log, signals
from scrapy.xlib.pydispatch import dispatcher
import os
import threading

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


def call(spider_name, **spider_kwargs):
    args = ''
    if spider_kwargs:
        for k in spider_kwargs:
            args += '-a %s=%s ' % (k, str(spider_kwargs[k]))
    cmd = 'scrapy crawl %s %s'  % (spider_name, args)
#     threading.Thread(target=os.popen, kwargs={'command' : 'scrapy crawl %s %s'  % (spider_name, args)})
    print 'spider %s with args: %s will start.' % (spider_name, args)
    os.popen(cmd)

