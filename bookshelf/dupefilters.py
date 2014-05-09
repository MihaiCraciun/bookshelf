# encoding: utf-8
# Created on 2014-5-9
# @author: binge

import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from scrapy.dupefilter import RFPDupeFilter
# import md5
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

class UnFilterDupeFilter(RFPDupeFilter):
    '''
    this class extends scrapy.dupefilter.RFPDupeFilter(default filter the duplicate request),
    for un filter the duplicate request. overwrite function request_fingerprint, every single time
    this function will return the different value.

    and function request_seen is used to judge is current request having been crawled yet, in this,
    we just return False.
    '''

    def request_seen(self, request):
        return False

    def request_fingerprint(self, request):
        return md5(request._get_url() + str(time.time()))
