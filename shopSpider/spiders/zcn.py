# -*- coding: utf-8 -*-
import scrapy


class ZcnSpider(scrapy.Spider):
    name = 'zcn'
    allowed_domains = ['http://www.hhanbag.com']
    start_urls = ['http://www.hhanbag.com']

    config = {}          # settings自定义配置项
    filter_main_navBars = []    #  过滤后的一级菜单
    category_urls = []   # 需要爬取的分类链接

    def __init__(self, config):
        self.config = config

    @classmethod
    def from_crawler(cls, crawler):
        return cls(config=crawler.settings.get('SPADER_SHOP_CONFIG'))  


    def parse(self, response):
        # 获取一级菜单
        self.getMainNavBars(response)

        # 获取分类链接
        self.getCategoryUrls()

        # 请求商品列表
        for url in self.category_urls:
            yield scrapy.Request(url=url, callback=self.handleProductList, dont_filter=True)
            

    # 获取一级菜单
    def getMainNavBars(self, response):
        main_navBars = response.css(self.config['mainNavBarSelector'])
        for index,navBar in enumerate(main_navBars):
            # 过滤一级菜单导航，去掉不需要的
            if index  not in self.config['mainNavBarFilterByIndex']:
                self.filter_main_navBars.append(navBar)

    
    # 获取分类链接
    def getCategoryUrls(self):
        for navBar in self.filter_main_navBars:
            hrefs = navBar.css('a::attr(href)').extract()
            for href in hrefs:
                self.category_urls.append(href)
                

    # 处理商品列表
    def handleProductList(self, response):
        print(response)