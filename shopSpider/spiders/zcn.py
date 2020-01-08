# -*- coding: utf-8 -*-
import scrapy


class ZcnSpider(scrapy.Spider):
    name = 'zcn'
    allowed_domains = ['http://hhanbag.com/']
    start_urls = ['http://http://hhanbag.com/']

    def parse(self, response):
        pass
