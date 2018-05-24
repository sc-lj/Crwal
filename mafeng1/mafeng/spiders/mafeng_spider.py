#coding:utf-8

from mafeng.items import MafengItem_area
import scrapy,re,time,random
from scrapy.selector import Selector
import json,math
from scrapy.spiders import Spider
from scrapy.http import FormRequest

class MafengSpider(Spider):
    name ='mafeng'
    allowed_domains=['mafengwo.cn']
    # 通过调用 start_requests() 方法（默认情况下）为 start_urls 中指定的URL生成初始的 Request 以及将 parse 方法作为请求的回调函数。
    start_urls=['http://www.mafengwo.cn/mdd/']
    domain_url='http://www.mafengwo.cn'

    CommentList_url='http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi'
    gonglve_url = domain_url + '/ajax/router.php'  # 目的地页面

    # 爬取目的地
    def parse(self, response):
        hrefs=response.xpath('.//div[@class="row row-hot"]/div/div[3]/div[1]/div/dl[position()>0]/dd/a')
        for href in hrefs:
            hr=href.xpath('./@href').extract()[0]
            location_num=hr.split('/')[-1].split('.')[0]#地区编码
            if len(location_num)==0:
                continue
            location=href.xpath('.//text()').extract()[0]

            hotel_url=self.domain_url+'/hotel/%s'%location_num#对景区酒店的评论
            eat_url=self.domain_url+'/cy/%s/gonglve.html'%location_num #对目的地的美食评价


            yield FormRequest(self.gonglve_url,formdata={'iMddid':location_num,'iTagId':'0','iPage':'1','sAct':'KMdd_StructWebAjax|GetPoisByTag'},callback=self.parse_gonglve,
                                     meta={'location':location,'location_num':location_num,'page':'1'},method='POST',encoding='utf-8',dont_filter=True)

    # def start_requests(self):
    #     location_num='10065'
    #     location='北京'
    #     print location
    #     yield FormRequest(self.gonglve_url,formdata={'iMddid':location_num,'iTagId':'0','iPage':'1','sAct':'KMdd_StructWebAjax|GetPoisByTag'},callback=self.parse_gonglve,
    #                                  meta={'location':location,'location_num':location_num,'page':'1'},method='POST',encoding='utf-8')

    # 该函数返回的是评论页面
    def parse_gonglve(self,response):
        location=response.meta['location']
        page=int(response.meta['page'])
        location_num=response.meta['location_num']
        data=json.loads(response.text)
        data=data['data']

        lists=data['list']
        lists=Selector(text=lists)

        Scenics=lists.xpath('.//li')
        for scenic in Scenics:
            href=scenic.xpath('.//@href').extract()[0]
            Scenic_name=scenic.xpath('.//@title').extract()[0]#景区名
            Scenic_num = href.split('/')[-1].split('.')[0]#景区编码
            jQuery = ('jQuery181' + repr(random.random())).replace('.', '') + '_' + '%s' % int(time.time() * 100)

            yield FormRequest(self.CommentList_url, callback=self.parse_content,formdata={'params':'{"poi_id":"%s"}'%str(Scenic_num),
                                                                                                 '_':str(int(time.time()*100)),'callback':jQuery,},
                                     meta={'location':location,'Scenic_name':Scenic_name,'Scenic_num':str(Scenic_num),'page':str(page),'jQuery':jQuery},method='get',dont_filter=True)

        pages = data['page']
        if len(pages)!=0:
            pages=Selector(text=pages)
            all_pages=pages.xpath('.//div/span/span[1]/text()').extract()[0]#总共也多少页
            if page<int(all_pages):
                page+=1
                yield FormRequest(self.gonglve_url, formdata={'iMddid': str(location_num), 'iTagId': '0', 'iPage': str(page),
                                                            'sAct': 'KMdd_StructWebAjax|GetPoisByTag'},callback=self.parse_gonglve,method='post',
                                     meta={'location': location, 'location_num': str(location_num), 'page': page},dont_filter=True)

    # 解析评论数据
    def parse_content(self,response):
        item=MafengItem_area()
        location = response.meta['location']
        Scenic_name=response.meta['Scenic_name']
        Scenic_num=response.meta['Scenic_num']
        page = int(response.meta['page'])
        jQuery=response.meta['jQuery']

        content=response.text
        content=re.findall('jQuery\d+_\d+((?:.|\n)+)',content)[0][1:-2]
        content = json.loads(content)['data']
        comment_count=content['controller_data']['comment_count']
        pages=math.ceil(int(comment_count)/15.)

        html=content['html']
        html= Selector(text=html)
        tables=html.xpath('.//div[@class="rev-list"]/ul/li')
        for table in tables:
            Commenter_level=table.xpath('.//div[@class="user"]/span/text()').extract()[0]
            useful=table.xpath('./a[1]/span/text()').extract_first(0)
            Commenter =table.xpath('./a[2]/text()').extract()[0]
            star=table.xpath('./span/@class').extract()[0]
            star=re.findall('s-star(\d)',star)[0]
            Commenter_content=table.xpath('./p/text()').extract()[0]
            comment_time=table.xpath('./div[@class="info clearfix"]/span/text()').extract()[0]
            try:
                image_url=table.xpath('./div[@class="rev-img"]/a/img/@src').extract()
            except:
                image_url=None


            item['location']=location
            item['Scenic_name']=Scenic_name
            item['Commenter_level']=Commenter_level
            item['useful']=useful
            item['Commenter']=Commenter
            item['star']=star
            item['Commenter_content']=Commenter_content
            item['comment_time']=comment_time
            item['images_url']=image_url
            yield item

        if page<int(pages):
            time.sleep(random.uniform(3,10))
            page+=1
            yield FormRequest(self.CommentList_url, callback=self.parse_content,
                                     formdata={'params': '{"poi_id":"%s","page":%s,"just_comment":1}'%(str(Scenic_num),page),
                                               '_': str(int(time.time() * 100)), 'callback': jQuery},
                                     meta={'location': location, 'Scenic_name': Scenic_name,'Scenic_num':str(Scenic_num),'page':str(page),'jQuery':str(jQuery)},
                                     method='get')

