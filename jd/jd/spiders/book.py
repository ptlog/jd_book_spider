# -*- coding: utf-8 -*-
import scrapy
import copy
import json

from urllib import parse


class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['jd.com','p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        dt_list = response.xpath("//div[@class='mc']/dl/dt")
        for dt in dt_list:
            item = {}
            # 获取大分类
            item['b_cate'] = dt.xpath("./a/text()").extract_first()

            # 获取小分类
            em_list = dt.xpath("following-sibling::dd[1]/em")
            for em in em_list:
                item['s_cate'] = em.xpath("./a/text()").extract_first()
                item['s_cate_href'] = em.xpath("./a/@href").extract_first()
                # print(item)
                # 抛出url相应的request对象，交给引擎处理
                if item['s_cate_href'] is not None:
                    item['s_cate_href'] = 'http:' + item['s_cate_href']
                    # print(item)
                    # print('if__inner')
                    yield scrapy.Request(
                        item['s_cate_href'],
                        callback=self.parse_book_list,
                        meta={'item':copy.deepcopy(item)}
                    )

    def parse_book_list(self, response):
        '''请求小分类的url地址，处理返回的相应'''
        print('-------'*10)
        item = response.meta['item']
        li_list = response.xpath("//div[@id='plist']/ul/li")
        for li in li_list:
            # 获取书本的图片
            item['book_img'] = li.xpath(".//div[@class='p-img']/a/img/@src").extract_first()
            if item['book_img'] is None:
                item['book_img'] = 'https' + li.xpath(".//div[@class='p-img']//img/@data-lazy-img").extract_first()
                # print(item)
                # print('8'*100)
                # return
            # 获取书名
            item['book_name'] = li.xpath(".//div[@class='p-name']/a/em/text()").extract_first().strip()
            # 获取作者
            item['author'] = li.xpath(".//div[@class='p-bookdetails']/span[@class='p-bi-name']/span/a/text()").extract()
            # if item['author'] is None:
                # print('88888')
            # 获取出版社
            item['publish'] = li.xpath(".//div[@class='p-bookdetails']/span[@class='p-bi-store']/a/@title").extract_first()
            # 获取出版日期
            item['publish_date'] = li.xpath(".//div[@class='p-bookdetails']/span[@class='p-bi-date']/text()").extract_first().strip()
            # 获取sku_id， 目的是为了获取价格而获取的
            item['sku_id'] = li.xpath("./div/@data-sku").extract_first()

            yield scrapy.Request(
                'https://p.3.cn/prices/mgets?skuIds=J_{}%2C'.format(item['sku_id']),
                callback=self.parse_price,
                meta={'item':copy.deepcopy(item)}
            )

        # 翻页
        next_url = response.xpath("//a[text()='下一页']/@href").extract_first()
        # print(next_url)
        if next_url is not None:
            next_url = parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item':copy.deepcopy(item)}
            )

    def parse_price(self, response):
        '''获取价格'''
        item = response.meta['item']
        item['price'] = json.loads(response.body.decode())[0]['p']
        yield item

