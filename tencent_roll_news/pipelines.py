# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
import os


class TencentRollNewsPipeline(object):

    def __init__(self):
        self.current_dir = os.getcwd()

    def process_item(self, item, spider):
        print(item['category'])
        dir_path = self.current_dir + '/doc' '/' + item['category'] + '/' + item['date']
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        news_file_path = dir_path + '/' + item['newsId'] + '.json'
        if os.path.exists(news_file_path) and os.path.isfile(news_file_path):
            print('---------------------------------------')
            print(item['newsId'] + '.json exists, not overriden')
            print('---------------------------------------')
            return item

        news_file = codecs.open(news_file_path, 'w', 'utf8')
        line = json.dumps(dict(item),ensure_ascii=False)
        # print('=======')
        # print(line)
        # print('=======')
        news_file.write(line)
        news_file.close()
        return item
