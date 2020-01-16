# -*- coding: utf-8 -*-
import scrapy
from shopSpider.items import ProductItem

class ZcnSpider(scrapy.Spider):
    name = 'zcn'
    allowed_domains = []
    start_urls = []
    config = {}                 # settings自定义配置项

    def __init__(self, config):
        self.allowed_domains = config['domain']
        self.start_urls = config['startUrls']
        self.config = config

    @classmethod
    def from_crawler(cls, crawler):
        return cls(config=crawler.settings.get('SPADER_SHOP_CONFIG'))  


    def parse(self, response):
        # 获取分类链接
        category_urls = self.getCategoryUrls(response)   

        # 根据商品分类请求商品列表
        for url in category_urls[0:1]:
            yield scrapy.Request(url=url, callback=self.handleProductList, dont_filter=True)

    #处理菜单并获取分类链接
    def getCategoryUrls(self, response):
        filter_main_navBars = []                    # 过滤后的一级菜单
        category_urls = []                          # 需要爬取的分类链接

        # 获取一级菜单
        main_navBars = response.css(self.config['mainNavBarSelector'])
        for index,navBar in enumerate(main_navBars):
            # 过滤一级菜单导航，去掉不需要的
            if index not in self.config['mainNavBarFilterByIndex']:
                filter_main_navBars.append(navBar)
        
        # 根据过滤后的一级菜单获取所有分类链接
        for navBar in filter_main_navBars:
            hrefs = navBar.css('a::attr(href)').extract()
            category_urls.extend(hrefs)
        
        return category_urls

    # 处理商品列表
    def handleProductList(self, response):
        list_urls = response.css(self.config['listUrlsSelector']).extract()         # 需要爬取的列表链接

        # 根据商品列表请求商品详情
        for url in list_urls: 
            yield scrapy.Request(url=url, callback=self.handleProductDetails, dont_filter=True)

    
    # 处理商品详情
    def handleProductDetails(self, response):
        item = ProductItem()
        item['categories'] = response.css(self.config['breadcrumbSelector']).extract()[1:]         # 根据面包屑获取分类等级数组
        item['products_price'] = response.css(self.config['productsPriceSelector']).extract_first().replace('$','').replace(' ','')   # 爬取的价格去掉 $
        item['products_name'] = response.css(self.config['productsNameSelector']).extract_first()
        item['products_description'] = response.css(self.config['productsDescriptionSelector']).extract_first()
        yield item
