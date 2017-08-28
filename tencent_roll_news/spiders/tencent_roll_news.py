#!usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author: Jeff Zhang
@date:   2017-08-28
"""

from scrapy.selector import Selector
import json
import re
from scrapy import Request, Spider
import time
import datetime
from tencent_roll_news.items import TencentRollNewsItem

def ListCombiner(lst):
    string = ""
    for e in lst:
        string += e
    return string.replace(' ','').replace('\n','').replace('\t','')\
        .replace('\xa0','').replace('\u3000','').replace('\r','')


class TencentNewsSpider(Spider):
    name = 'tencent_news_spider'
    # allowed_domains = ['news.qq.com']
    start_urls = ['http://news.qq.com/articleList/rolls/']
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'

    list_url = 'http://roll.news.qq.com/interface/cpcroll.php?callback=rollback&site={class_}&mode=1&cata=&date={date}&page={page}&_={time_stamp}'
    date_time = datetime.datetime.now().strftime('%Y-%m-%d')
    time_stamp = int(round(time.time()*1000))
    item_num = 0

    def start_requests(self):
        categories = ['news', 'ent', 'sports', 'finance', 'tech', 'games', 'auto', 'edu', 'house']
        for category in categories:
            yield Request(self.list_url.format(class_=category, date=self.date_time, page='1', time_stamp=str(self.time_stamp)), callback=self.parse_list, dont_filter=True, meta={'category':category})

    def parse_list(self, response):
        results = json.loads(response.text[9:-1])
        article_info = results['data']['article_info']
        category = response.meta['category']
        for element in article_info:
            time_ = element['time']
            title = element['title']
            column = element['column']
            url = element['url']
            if column != u'图片':
                yield Request(url, callback=self.parse_news, meta={'column':column,
                                                          'url':url,
                                                          'title':title,
                                                          'time':time_,
                                                          'category':category
                                                         }, dont_filter=True)
        list_page = results['data']['page']
        list_count = results['data']['count']
        if list_page < list_count:
            time_stamp = int(round(time.time() * 1000))
            yield Request(self.list_url.format(class_=category, date=self.date_time, page=str(list_page+1), time_stamp=str(time_stamp)), callback=self.parse_list, meta={'category':category}, dont_filter=True)

    def parse_news(self, response):
        sel = Selector(response)

        url = response.meta['url']
        title = response.meta['title']
        column = response.meta['column']
        time_ = response.meta['time']
        category = response.meta['category']

        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2)
        date = date[0:4] + '/' + date[4:6] + '/' + date[6:]
        newsId = pattern.group(3)
        contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])


        try:
            cmt = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()').extract()[0]
            cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
        except:
            item = TencentRollNewsItem()
            item['source'] = source
            item['category'] = category
            item['time'] = time_
            item['date'] = date
            item['contents'] = contents
            item['title'] = title
            item['url'] = url
            item['newsId'] = newsId
            item['comments'] = 0
            item['column'] = column
            return item

        comment_url = 'http://coral.qq.com/article/{}/comment?commentid=0&reqnum=1&tag=&callback=mainComment&_=1389623278900'.format(cmt_id)
        yield Request(comment_url, callback=self.parse_comment, dont_filter=True, meta={'source': source,
                                                                               'date': date,
                                                                               'newsId': newsId,
                                                                               'url': url,
                                                                               'title': title,
                                                                               'contents': contents,
                                                                               'time': time_,
                                                                               'column': column,
                                                                               'category': category
                                                                               })
    def parse_comment(self, response):
        if re.findall(r'"total":(\d*)\,', response.text):
            comments = re.findall(r'"total":(\d*)\,', response.text)[0]
        else:
            comments = 0
        item = TencentRollNewsItem()
        item['category'] = response.meta['category']
        item['source'] = response.meta['source']
        item['time'] = response.meta['time']
        item['date'] = response.meta['date']
        item['contents'] = response.meta['contents']
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['newsId'] = response.meta['newsId']
        item['comments'] = comments
        item['column'] = response.meta['column']
        return item