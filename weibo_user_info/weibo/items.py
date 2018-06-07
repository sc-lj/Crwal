# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    level = scrapy.Field()
    nick_name = scrapy.Field()
    auth_info = scrapy.Field()
    sex = scrapy.Field()
    addr = scrapy.Field()
    birthday = scrapy.Field()

    def get_sql(self):
        sql = """
        INSERT INTO user_info 
        VALUES(%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE level=VALUES(level)
        """
        values = (
        self['nick_name'], self['level'], self['auth_info'], self['sex'], self['addr'], self['birthday'])
        return sql.strip(), values
