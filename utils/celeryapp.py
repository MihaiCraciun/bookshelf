# encoding: utf-8
# Created on 2014-5-21
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from celery import Celery
from settings import celery_broker, celery_backend, celery_include,\
    celery_proj

app = Celery(celery_proj,
             broker=celery_broker,
             backend=celery_backend,
             include=celery_include)

app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)
