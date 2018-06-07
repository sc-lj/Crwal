# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import requests
import json
import logging


class UserAgentMiddleware(object):
    def __init__(self):
        self.ua = UserAgent()
        self.logger = logging.getLogger(__name__)

    def process_request(self, request, spider):
        ua = self.ua.random
        self.logger.debug("Using User-Agent " + ua)
        request.headers['User-Agent'] = ua


class CookiesMiddleware(object):
    def __init__(self, weibo_cookie_url):
        self.weibo_cookie_url = weibo_cookie_url
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings.get('WEIBO_COOKIE_URL'))

    def get_random_cookie(self, url):
        r = requests.get(url)
        return r.text

    def process_request(self, request, spider):
        cookie = self.get_random_cookie(self.weibo_cookie_url)
        self.logger.debug("Using Cookie " + cookie)
        request.cookies = json.loads(cookie)

