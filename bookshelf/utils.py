# encoding: utf-8
# Created on 2014-5-7
# @author: binge

import sys
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

def time_2_str(time = datetime.datetime.now(), frt = '%Y-%m-%d %H:%M:%S'):
    '''
        this function parse time obj to str by frt parameter,
        parameter time is default datetime.datetime.now(),
        and parameter frt default %Y-%m-%d %H:%M:%S
    '''
    return time.strftime(frt)
