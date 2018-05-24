# coding:utf-8
# 过滤器，url去重

from scrapy.dupefilter import BaseDupeFilter
from w3lib.url import canonicalize_url#canonicalize_url格式化url
#ScalableBloomFilter是一个不定容量的布隆过滤器，它可以不断添加元素。BloomFilter是一个定容的过滤器，error_rate是指最大的误报率是0.1%
from pybloom import ScalableBloomFilter
import hashlib,redis
from scrapy.utils.request import request_fingerprint

class URLBloomFilter(BaseDupeFilter):
    def __init__(self,host,port):
        self.urls_sbf=ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        self.host=host
        self.port=port
        self.client = redis.Redis(self.host, self.port)


    @classmethod
    def from_settings(cls, settings):
        return cls(host=settings.get('FILTER_HOST'),
                   port=settings.get('FILTER_PORT'))


    def request_seen(self, request):
        fp=hashlib.sha1()
        fp.update(canonicalize_url(request.url))
        url_sha1=fp.hexdigest()
        if url_sha1 in self.urls_sbf:
            return True
        else:
            self.urls_sbf.add(url_sha1)



# 在setting中，DUPEFILTER_CLASS="mafeng.mafeng.bloomRedisFilter.URLBloomFilter"



