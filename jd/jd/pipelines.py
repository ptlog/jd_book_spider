# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class JdPipeline(object):
    def open_spider(self, spider):
        '''连接本地monggodb客户端'''
        # 使用open_spider 目的是， scrapy框架一开始会启用open_spider这个方法， 只执行一次，
        # 目的是为了存储信息的时候，不会反复的打开连接数据库
        client = MongoClient()
        self.collection = client['jd']['book']

    def process_item(self, item, spider):
        print(item)
        self.collection.insert(item)
