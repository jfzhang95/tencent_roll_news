# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field, Item

class TencentRollNewsItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()
    date = Field()
    time = Field()
    title = Field()
    newsId = Field()
    contents = Field()
    comments = Field()
    source = Field()
    column = Field()
