# encoding: utf-8
# Created on 2014-5-21
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from celeryapp import app
from utils.spider_caller import SpiderCaller

@app.task
def start_spider(spider_name, **spider_kwargs):
    SpiderCaller().run(spider_name, **spider_kwargs)
    return 'complete.'
