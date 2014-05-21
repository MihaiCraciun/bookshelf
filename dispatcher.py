# encoding: utf-8
# Created on 2014-5-21
# @author: binge

import sys
from utils.celery_call import call, update_celery_tasks_status
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

import os
# sys.path.insert(0, os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))
from settings import source_home_spiders

def run_worker():
    celery_exe = "d:\\soft\\Python27\\Scripts\\celery.exe"
    os.popen(celery_exe + ' worker --app=utils.celeryapp:app -l info -f ./log/celery.log &')
    print "Wordker started."

def start():
#     run_worker()
    call('qd')
#     call('qdhome', src='http://www.qidian.com/Book/147919.aspx', b_id='2acf3455598bc4839218e8035e8ccf3a')
#     for sn in source_home_spiders:
#         call(sn)

    update_celery_tasks_status()

if __name__ == '__main__':
    start()
