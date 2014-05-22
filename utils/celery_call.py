# encoding: utf-8
# Created on 2014-5-21
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import logging
logging.basicConfig()
from apscheduler.scheduler import Scheduler
from utils.conns_helper import RedisHelper
from utils.common import RedisStrHelper
from settings import source_home_spiders
from utils.celeryapp import app
from utils.celery_tasks import start_spider
from celery.events.state import State

def get_tasks_uuid(task_type):
    tasks = State().tasks_by_type(task_type)
    uuids = set()
    for uuid, _ in tasks:
        uuids.add(uuid)
    return uuids

def delay_crawl(spider_name, **spider_kwargs):
    return start_spider.delay(spider_name, **spider_kwargs) # @UndefinedVariable

def update_celery_tasks_status():
    schedudler = Scheduler(daemonic = False)

    @schedudler.cron_schedule(second='*/30', max_instances=3)
    def update_job():
        infos = RedisHelper.get_all_celery_tasks_info()
        res_ids = get_tasks_uuid('start_spider')
        for res_id in infos:
            is_complete = False
            info = infos[res_id]
            spider_name = RedisStrHelper.split(info)[1]
            if res_id in res_ids:
                res = app.AsyncResult(res_id)
                if res.state == 'SUCCESS':
                    is_complete = True
                else:
                    if res.state == 'FAILURE':
                        print res.trackback()
                        ## TODO: warning
                        pass
                    RedisHelper.update_celery_task_status(res_id, res.state)
            else:
                is_complete = True
            if is_complete:
                if spider_name in source_home_spiders:
    #                     time.sleep(1 * 60)
                        call(spider_name)
                RedisHelper.del_celery_task_status(res_id)

    schedudler.start()

def call(spider_name, **spider_kwargs):
    res = delay_crawl(spider_name, **spider_kwargs)
    RedisHelper.set_celery_task_info(res.id, spider_name, res.state, **spider_kwargs)
    update_celery_tasks_status()
