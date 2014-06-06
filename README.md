
# bookshelf



## Usage
本程序由python语言编写.<br/>
    1. 依赖库见([dependencies](https://github.com/zhiying8710/bookshelf/blob/master/dependencies))<br/>
    2. 使用scrapy爬虫框架,mongo为数据存储介质,redis作为缓存, 利用celery+redis实现消息队列.<br/>
    3. 启动<br/>
       A. 修改配置: ([settings.py](https://github.com/zhiying8710/bookshelf/blob/master/settings.py))<br/>
       B. easy_install celery 或 pip install celery 后进入到项目根目录, 运行celery worker --app=utils.celeryapp:app -l info -f ./log/celery.log & 启动celery. <br/>
       C. 运行脚本([dispatcher.py](https://github.com/zhiying8710/bookshelf/blob/master/dispatcher.py)) 启动整个程序.<br/>



## Developing



### Tools

Created with [Nodeclipse](https://github.com/Nodeclipse/nodeclipse-1)
 ([Eclipse Marketplace](http://marketplace.eclipse.org/content/nodeclipse), [site](http://www.nodeclipse.org))

Nodeclipse is free open-source project that grows with your contributions.
