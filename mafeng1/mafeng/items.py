# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


# 有关景区评论的item
class MafengItem_area(Item):
    # define the fields for your item here like:
    Scenic_name = Field()#景点名称
    location=Field()#景点地址
    Commenter=Field()#评论者昵称
    Commenter_level=Field()#评论者等级
    star=Field()#评论者打的分数
    useful=Field()#评论的点赞数
    Commenter_content=Field()#评论者的评论内容
    comment_time=Field()#评论时间
    images_url=Field()#评论者上传的图片url
    images=Field()#评论者上传的图片
    mongodb_id=Field()




class MafengItem_hotel(Item):
    location=Field()#景点地址
    hotel=Field()#景点酒店名称
    hotel_rate=Field()#酒店评分


