# encoding: utf-8
# Created on 2014-5-21
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import threading
from utils.conns_helper import RedisHelper
from utils import spider_caller
from settings import source_home_spiders, monitor_main_spider_queue,\
    search_spider_info_queue, update_site_spider_info_queue

def start():
#     spider_info = {'spider_name': 'lu5sea',  'b_id': 'ba7f10902f9e3ecf4c2bf083ae2d2989', 'b_name' : "永夜君王", 'b_author' : '烟雨江南'}
#     threading.Thread(target=spider_caller.call, kwargs=spider_info).start()
#     while 1:
#         pass
    rconn = RedisHelper.get_redis_conn()
    main_spiders = set([])
    for sn in source_home_spiders:
        threading.Thread(target=spider_caller.call, kwargs={'spider_name': sn}).start()
        main_spiders.add(sn)
        rconn.sadd(monitor_main_spider_queue, sn)
        sn = source_home_spiders[sn]
        threading.Thread(target=spider_caller.call, kwargs={'spider_name': sn}).start()
        main_spiders.add(sn)
        rconn.sadd(monitor_main_spider_queue, sn)
    while 1:
        for main_spider in main_spiders:
            if not rconn.sismember(monitor_main_spider_queue, main_spider):
                threading.Thread(target=spider_caller.call, kwargs={'spider_name': main_spider}).start()
        s_spider_info = rconn.spop(search_spider_info_queue)
        if s_spider_info:
            spider_info = eval(s_spider_info)
            threading.Thread(target=spider_caller.call, kwargs=spider_info).start()

        s_spider_info = rconn.spop(update_site_spider_info_queue)
        if s_spider_info:
            spider_info = eval(s_spider_info)
            threading.Thread(target=spider_caller.call, kwargs=spider_info).start()

if __name__ == '__main__':
    start()
