# -*- coding: utf-8 -*-
import scrapy


class ZcnSpider(scrapy.Spider):
    name = 'zcn'
    allowed_domains = ['http://hhanbag.com/']
    start_urls = ['http://hhanbag.com/']

    config = {}          # settings自定义配置项
    filter_main_navBars = []    #  过滤后的一级菜单
    category_urls = []   # 需要爬取的分类链接

    def __init__(self, config):
        self.config = config

    @classmethod
    def from_crawler(cls, crawler):
        return cls(config=crawler.settings.get('SPADER_SHOP_CONFIG'))  


    def parse(self, response):
        self.getMainCategory(response)
        

    # 获取一级菜单主分类
    def getMainCategory(self, response):
        main_navBars = response.css(self.config['mainNavBarSelector'])
        for index,navBar in enumerate(main_navBars):
            # 过滤一级菜单导航，去掉不需要的
            if index  not in self.config['mainNavBarFilterByIndex']:
                self.filter_main_navBars.append(navBar)
        
        print(self.category_urls)
