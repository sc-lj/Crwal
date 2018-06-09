# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from items import MafengItem_area,MafengItem_hotel
import pymongo
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from .scrapy_redis.BloomFilter import BloomFilter
import redis,time
import pickle,os,copy
path=os.getcwd()
os.chdir(path)

import logging
logger=logging.getLogger(__name__)

class MafengPipeline(object):
    def process_item(self, item, spider):
        return item

class MafengMongoPipline():
    @classmethod
    def from_crawler(cls,crawler):
        return cls(mongo_uri=crawler.settings.get('MONGO_HOST'),
                   mongo_port=crawler.settings.get('MONGO_PORT'))

    def __init__(self,mongo_uri,mongo_port):
        self.mongo_uri= mongo_uri
        self.mongo_port=mongo_port


    def open_spider(self,spider):
        self.client=pymongo.MongoClient(self.mongo_uri,self.mongo_port)
        self.db = self.client['mafeng']


    def process_item(self,item,spider):
        # 当item在spider中被收集后，都会调用这个方法
        if isinstance(item,MafengItem_area):
            collection='area'
        elif isinstance(item,MafengItem_hotel):
            collection='hotel'
        else:
            print('undefine item')
            return item

        try:
            self.db[collection].insert(dict(item))
            return item
        except Exception as e:
            return item

    def close_spider(self,spider):
        self.client.close()


class ImagesPipline(ImagesPipeline):
    default_headers = {
        'accept': 'image/webp,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'cookie': 'bid=yQdC/AzTaCw',
        'referer': '',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }
    def get_media_requests(self, item, info):

        image_url=item['images_url']
        if len(image_url)!=0:
            for url in image_url:
                self.default_headers['referer'] = url
                yield Request(url,headers=self.default_headers)

    '''
    get_media_requests请求完成后，其结果将会以2-元素的元组列表形式传送到 item_completed() 方法: 每个元组包含 (success, file_info_or_error)；
    result格式为：[(True,
  {'checksum': '2b00042f7481c7b056c4b410d28f33cf',
   'path': 'full/0a79c461a4062ac383dc4fade7bc09f1384a3910.jpg',
   'url': 'http://www.example.com/files/product1.pdf'}),
 (False,
  Failure(...))]
    '''
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['images'] = image_paths
        return item




class DataFilterPipline(object):
    logger = logger

    @classmethod
    def from_settings(cls,settings):
        host=settings.get('FILTER_HOST','localhost')
        port=settings.get('FILTER_PORT',6379)
        db=settings.get('FILTER_DB',1)
        pool = redis.ConnectionPool(host=host, port=port, db=db)
        newserver= redis.StrictRedis(connection_pool=pool)
        key='datafilter'
        bot_name=settings.get('BOT_NAME')
        serializer=settings.get('FILTER_SERIALIZER','%s.json'%bot_name)
        return cls(newserver,key,serializer)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def __init__(self,newserver,key,serializer):
        self.serializer=serializer
        self.server=newserver
        self.key=key
        self.bloom=BloomFilter(conn=newserver,key=key)
        # self.bloom=copy.deepcopy(bloom)


    def process_item(self, item, spider):
        # 这里需要深copy，不然插入mongo中有很多重复的，这是因为由于Spider的速率比较快，而scapy操作数据库操作比较慢，
        # 导致pipeline中的方法调用较慢，这样当一个变量正在处理的时候，一个新的变量过来，之前的变量的值就会被覆盖。
        # 比如pipline的速率是1TPS，而spider的速率是5TPS，那么数据库应该会有5条重复数据。
        anyItem = copy.deepcopy(item)
        Commenter_content=anyItem['Commenter_content'].strip()
        Commenter=anyItem['Commenter'].strip()
        Scenic_name=anyItem['Scenic_name'].strip()
        # fp=sha224()
        # fp.update(to_bytes(Scenic_name))
        # fp.update(to_bytes(Commenter_content))
        # fp.update(to_bytes(Commenter))
        # newdata=fp.hexdigest()
        newdata=''.join([Commenter_content,Commenter,Scenic_name]).encode('utf-8')
        if self.bloom.is_exist(newdata):
            msg = "content had crawled:%(Scenic)s ,%(content)s"
            self.logger.warning(msg, {'content':Commenter_content,'Scenic':Scenic_name})
            raise DropItem()
        else:
            self.bloom.add(newdata)
            return anyItem


