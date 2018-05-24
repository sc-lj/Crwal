# -*- coding: utf-8 -*-

# Scrapy settings for mafeng project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'mafeng'

SPIDER_MODULES = ['mafeng.spiders']
NEWSPIDER_MODULE = 'mafeng.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mafeng (+http://www.yourdomain.com)'

# Obey robots.txt rules
# 遵守机器人协议
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# 每次从调度中获取的最大请求数
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# 下载延迟
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY=True#如果为True，那么会随机等待时间范围[0.5*DOWNLOAD_DELAY,1.5*DOWNLOAD_DELAY]
# The download delay setting will honor only one of:
# 每个域名并发请求数
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
# 每个IP并发请求数
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# 禁止重定向
REDIRECT_ENBLED=False

# 重试的次数
RETRY_TIMES=3

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'mafeng.middlewares.MafengSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'mafeng.middlewares.MyCustomDownloaderMiddleware': 543,
    'mafeng.middlewares.RandomUserAgent':1,

}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# 更改ITEM_PIPELINES，指定保存数据库的类。item按数字从低到高的顺序，通过pipeline
ITEM_PIPELINES = {
    'mafeng.pipelines.DataFilterPipline':100,
    'mafeng.pipelines.ImagesPipline':150,
    'mafeng.pipelines.MafengMongoPipline':200,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# 自定义的去重方式
DUPEFILTER_CLASS="mafeng.scrapy_redis.dupefilter.RFPDupeFilter"

# 使用scrapy_redis搭建分布式爬虫的setting设置
# 官方文档为http://github.com/rmax/scrapy_redis

#使用scrapy_redis的调度器
SCHEDULER="mafeng.scrapy_redis.scheduler.Scheduler"

# 在redis中保持scrapy_redis用到的各个队列，从而允许暂停和暂停后恢复
SCHEDULER_PERSIST=True

# 使用scrapy_redis的去重
# DUPEFILTER_CLASS='scrapy_redis.dupefilter.RFPDupeFilter'

# 指定排序地址所用的队列,默认的是按照优先级排序
# SCHEDULER_QUEUE_CLASS='mafeng.scrapy_redis.queue.FifoQueue'
# 也可以指定按照先进先出
SCHEDULER_QUEUE_CLASS='mafeng.scrapy_redis.queue.SpiderQueue'
# 也可以指定后进先出
# SCHEDULER_QUEUE_CLASS='mafeng.scrapy_redis.queue.SpiderStack'
# 去调度器调用数据的话，如果为空，最多等待时间
# 这只有当SCHEDULER_QUEUE_CLASS设置为SpiderQueue或者SpiderStack时有效。
# SCHEDULER_IDLE_BEFORE_CLOSE=20


# 使用scrapy_redis的存储方式
# 将清除的项目在redis进行处理
# ITEM_PIPELINES={'scrapy_redis.pipelines.RedisPipeline':300}


# 序列化项目管道作为redis Key存储
# REDIS_ITEMS_KEY = '%(spider)s:items'

# 默认使用ScrapyJSONEncoder进行项目序列化
# You can use any importable path to a callable object.
# REDIS_ITEMS_SERIALIZER = 'json.dumps'

# #指定连接到redis时使用的端口和地址（可选）
# REDIS_HOST='127.0.0.1'#如果是其他电脑的话，改为部署了redis的电脑IP
# REDIS_PORT=6379

#指定用于连接redis的URL（可选）
#如果设置此项，则此项优先级高于设置的REDIS_HOST 和 REDIS_PORT
# 在分布式爬虫时，如果部署了master-slave，在redis_url 中填入slave端url
# 如果只部署了master一台主机的，REDIS_URL可以去掉或者写None
# REDIS_URL=None
# REDIS_PARAMS={}

#默认使用ScrapyJSONEncoder进行项目序列化
#You can use any importable path to a callable object.
# REDIS_ITEMS_SERIALIZER = 'mafeng.dumps'

# REDIS_URL='redis://user:pass@hostname:6379'
# REDIS_PARAMS['password']=''

#设置redis使用utf-8之外的编码
#REDIS_ENCODING = 'latin1'

# 在spider中如果继承了RedisSpider或者RedisCrawlSpider定义 start_usls键
# 这样在master中执行scrapy mafeng: start_urls  (url)来启动scrapy
#REDIS_START_URLS_KEY = '%(name)s:start_urls'


# 去重队列信息
# 如果有种子队列，这些参数名要修改，而且
# 原先的REDIS_HOST、REDIS_PORT只负责种子队列；由此种子队列和去重队列可以分布在不同的机器上。
REDIS_URL=None
REDIS_HOST='localhost'
REDIS_PORT=6379
REDIS_DB=0
REDIS_CLS='redis.Redis'

# 新增如下mongo设置
# Mongo 的主机IP
MONGO_HOST='127.0.0.1'#如果是其他电脑的话，改为部署了MONGO的电脑IP
MONGO_PORT=27017

# MONGO的数据库名
MONGO_DB='mafeng'
# MONGO中的数据集名
MONGO_COLL='user'
# MONGO_USER='username'
# MONGO_PSW='password'

# 设置日志级别,[critical,error,warning,info,debug]
# LOG_LEVEL='INFO'
# # 日志文件名
# LOG_FILE='mafeng.log'
# # 日志输出格式
# LOG_FORMAT='%(levelname)s %(asctime)s %(name)s:%(moduls)s:%(funcName)s:%(lineno)s:%(exc_info)s %(message)s'
# # 日志的字符编码
# LOG_ENCODING='utf-8'


# 新增PHANTOMJS_PATH设置，用于模拟浏览器获取验证码并登陆。
# PHANTOMJS_PATH=''


IMAGES_STORE = '/Users/lj/image'# 图片存储路径


# 图片保存的时间
# IMAGES_EXPIRES = 30

# 图片缩略图
# IMAGES_THUMBS = {
#      'big': (270, 270)
# }

IMAGES_MIN_HEIGHT = 0
IMAGES_MIN_WIDTH = 0



