# Scrapy settings for bookshelf project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

BOT_NAME = 'bookshelf'

SPIDER_MODULES = [
                  'spiders.source',
                  'spiders.home',
                  'spiders.search'
                  ]
NEWSPIDER_MODULE = 'spiders'
ITEM_PIPELINES = {
    'pipelines.BookPipeline' : 500,
    'pipelines.BookDescPipeline' : 501,
    'pipelines.SectionsPipeline' : 502,
    'pipelines.UpdateSiteBookPipeline' : 503,
    'pipelines.DropPipeline' : 510
}
DOWNLOAD_TIMEOUT = 30
CONCURRENT_REQUESTS = 128
COOKIES_ENABLED = False
DUPEFILTER_DEBUG = True
DUPEFILTER_CLASS = 'dupefilters.UnFilterDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79 Safari/535.11'
DEFAULT_REQUEST_HEADERS = {
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3',
                           'Accept-Encoding': 'gzip,deflate,sdch',
                           'Accept-Language': 'zh-CN,zh;q=0.8',
                           'Connection': 'keep-alive'
                           }

LOG_ENABLED = True
LOG_FILE = './log/bookshelf.log'
LOG_LEVEL = 'DEBUG'

MEMDEBUG_NOTIFY = ['zhiying8710@hotmail.com']
ROBOTSTXT_OBEY = False

every_crawl_timedelta_mins = 3
source_spider_sleep_secs = 60 * 10

# config
sea_ingrone_spiders = set(['qdhome', 'zhhome', 'cshome', 'k17home'])
source_home_spiders = {
                       'qd' : 'qdhome',
                       'zh' : 'zhhome',
                       'cs' : 'cshome',
                       'k17' : 'k17home'
                       }

search_spider_names = {
                        'qdhome' : 'qdsea',
                        'zhhome' : 'zhsea',
                        'cshome' : 'cssea',
                        'k17home' : 'k17sea',
                        'lu5home' : 'lusea',
                        'bxwxhome' : 'bxwxsea',
                        'ranwenhome' : 'ranwensea',
                        'fqxswhome' : 'fqxswsea'
                        }
search_spider_info_queue = '__sea_spider_info_queue_'
update_site_spider_info_queue = '__update_site_spider_info'
####################################################
spider_redis_queues = {
                       'qdhome' : '__qidian_home_queue',
                       'zhhome' : '__zongheng_home_queue',
                       'cshome' : '__chuangshi_home_queue',
                       'k17home' : '__k17_home_queue'
                       }


book_no_home_url_val = 'NONE'

unupdate_retry_queue = '__unupdate_retry_queue'
crawling_key_prefix = '__crawling_'
crawling_key_expire = 3 * 60  # this must less than source_spider_sleep
last_crawl_time_key = '__last_crawl_time'
celery_task_info_key = '__celery_task_info'

monitor_main_spider_queue = '__monitor_main_spider_queue'

user_favos_update_counts_key_prefix = '__user_favos_update_counts_'

mongo_host = '127.0.0.1'
mongo_port = 27017
redis_host = '127.0.0.1'
redis_port = 6379
redis_def_db = 0
redis_sep = ':::'

celery_proj = "bookshelf"
celery_broker = "redis://"
celery_backend = "redis://"
celery_include = ['utils.celery_tasks']
