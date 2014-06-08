# encoding: utf-8
# Created on 2014-5-21
# @author: binge

import sys
import threading
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from utils import spider_caller
from settings import source_home_spiders


def start():
#     for sn in source_home_spiders:
#         spider_caller.call(sn)
#         spider_caller.call(source_home_spiders['sn'])
    threading.Thread(target=spider_caller.call, kwargs={'spider_name': 'cs'}).start()
#     threading.Thread(target=spider_caller.call, kwargs={'spider_name': 'k17home'}).start()
    while 1:
        pass

if __name__ == '__main__':
    start()
