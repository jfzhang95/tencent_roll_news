#!usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author: Jeff Zhang
@date:   2017-08-28
"""

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
import json
import re
from scrapy import Request, Spider
import time
import datetime
import requests
from tencent_roll_news.items import TencentRollNewsItem

def ListCombiner(lst):
    string = ""
    for e in lst:
        string += e
    return string.replace(' ','').replace('\n','').replace('\t','')\
        .replace('\xa0','').replace('\u3000','').replace('\r','')


class TencentNewsSpider(Spider):
    name = 'tencent_news_spider'
    allowed_domains = ['news.qq.com']
    start_urls = ['http://news.qq.com/articleList/rolls/']
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'

    list_url = 'http://roll.news.qq.com/interface/cpcroll.php?callback=rollback&site=news&mode=1&cata=&date={date}&page={page}&_={time_stamp}'
    date_time = datetime.datetime.now().strftime('%Y-%m-%d')
    time_stamp = int(round(time.time()*1000))
    def start_requests(self):
        yield Request(self.list_url.format(date='2017-06-07', page='1', time_stamp=str(self.time_stamp)), self.parse_list)

    def parse_list(self, response):
        results = json.loads(response.text[9:-1])
        article_info = results['data']['article_info']
        for element in article_info:
            time_ = element['time']
            title = element['title']
            column = element['column']
            url = element['url']
            yield Request(url, self.parse_news, meta={'column':column,
                                                      'url':url,
                                                      'title':title,
                                                      'time':time_
                                                      })
        list_page = results['data']['page']
        list_count = results['data']['count']
        if list_page < list_count:
            time_stamp = int(round(time.time() * 1000))
            yield Request(self.list_url.format(date='2017-06-07', page=str(list_page+1), time_stamp=str(time_stamp)), self.parse_list)

    def parse_news(self, response):
        sel = Selector(response)
        item = TencentRollNewsItem()

        url = response.meta['url']
        title = response.meta['title']
        column = response.meta['column']
        time_ = response.meta['time']

        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2)
        date = date[0:4] + '/' + date[4:6] + '/' + date[6:]
        newsId = pattern.group(3)
        contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])

        item['source'] = source
        item['time'] = time_
        item['date'] = date
        item['contents'] = contents
        item['title'] = title
        item['url'] = url
        item['newsId'] = newsId
        item['column'] = column
        return item

        # if sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()'):
        #     cmt = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()').extract()[0]
        #     if re.findall(r'cmt_id = (\d*);', cmt):
        #         cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
        #         comment_url = 'http://coral.qq.com/article/{}/comment?commentid=0&reqnum=1&tag=&callback=mainComment&_=1389623278900'.format(cmt_id)
        #         yield Request(comment_url, self.parse_comment, meta={'source': source,
        #                                                              'date': date,
        #                                                              'newsId': newsId,
        #                                                              'url': url,
        #                                                              'title': title,
        #                                                              'contents': contents,
        #                                                              'time': time_,
        #                                                              'column': column,
        #                                                              })

        # else:
        #     item['source'] = source
        #     item['time'] = time_
        #     item['date'] = date
        #     item['contents'] = contents
        #     item['title'] = title
        #     item['url'] = url
        #     item['newsId'] = newsId
        #     item['comments'] = 0
        #     item['column'] = column
        #     return item



    def parse_comment(self, response):
        if re.findall(r'"total":(\d*)\,', response.text):
            comments = re.findall(r'"total":(\d*)\,', response.text)[0]
        else:
            comments = 0
        item = TencentRollNewsItem()
        print(response.text)
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