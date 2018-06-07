# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from ..items import WeiboItem
import re
import json
from ..settings import START_USER


class WeiboUserSpider(CrawlSpider):
    name = 'weibo_user'
    allowed_domains = ['weibo.cn']
    start_urls = ['https://weibo.cn/u/{user}'.format(user=START_USER)]


    rules = (
        Rule(LinkExtractor(allow=('/\d+/info$',)), callback='parse_user_info'),
        Rule(LinkExtractor(allow=('/\d+/follow$',))),
        Rule(LinkExtractor(allow=('/\d+/fans$',))),
        Rule(LinkExtractor(allow=('https://weibo.cn/u/\d+$',))),
        Rule(LinkExtractor(allow=('https://weibo.cn/\d+$',))),
        Rule(LinkExtractor(allow=('/\d+/follow?page=\d+$',))),
        Rule(LinkExtractor(allow=('/\d+/fans?page=\d+$',)))
    )

    def parse_user_info(self, response):
        item = WeiboItem()
        level = response.xpath('/html/body/div[5]/text()').extract_first()
        if re.search('\d+', level):
            level = re.search('(\d+)', level).group(1)
        else:
            level = '0'
        item['level'] = level
        info = response.xpath('/html/body/div[7]/text()').extract()

        """注意一定要写ensure_ascii=False，否则会出现乱码问题"""
        temp = json.dumps(info, ensure_ascii=False)
        temp = temp.replace('昵称', 'nick_name').replace('认证', 'auth_info').replace('性别', 'sex').replace('地区', 'addr').replace('生日', 'birthday')
        info = json.loads(temp)
        for x in info:
            li = x.split(':')
            if len(li) == 2 and li[0] in item.fields:
                item[li[0]] = li[1]
        for field in item.fields:
            if field not in item.keys():
                item[field] = ''

        yield item
