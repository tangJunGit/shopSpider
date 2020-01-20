# -*- coding: utf-8 -*-
import scrapy
from shopSpider.items import ProductItem

class ZcnSpider(scrapy.Spider):
    name = 'zcn'
    allowed_domains = ["hermesprice.com"]
    start_urls = ['http://www.hermesprice.com']

    # ========= 自定义配置项 =============
    config = {
        ### ==========   菜单导航条
        # 一级菜单导航通过index过滤
        'mainNavBarFilterByIndex': [0],          
        # 一级菜单导航选择器          
        'mainNavBarSelector': '#nav>li',       

        ### ==========    商品列表
        # 商品列表链接选择器
        'listUrlsSelector': '.category-products .item>a::attr("href")',     
        # 商品列表下一页按钮选择器
        'listNextSelector': '.next-page>a::attr("href")',         

        ### ==========    商品分类
        # 商品分类选择器
        'breadcrumbSelector': '.breadcrumbs>ul>li>a::text',           

        ### ==========    商品详情
        # 商品价格选择器
        'productsPriceSelector': '.price-box .price::text',          
        # 商品名称选择器                        
        'productsNameSelector': '.product-name-main>h2::text',        
        # 商品描述选择器         
        'productsDescriptionSelector': '.wk_details_description',       
        # 商品图片选择器    
        'productsImagesSelector': '.product-img-box .slide img::attr("src")',  
    }

    def parse(self, response):
        # 获取分类链接
        category_urls = self.getCategoryUrls(response)   

        # 根据商品分类请求商品列表
        for url in category_urls:
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
        # 需要爬取的列表链接
        list_urls = response.css(self.config['listUrlsSelector']).extract()         

        # 根据商品列表请求商品详情
        for url in list_urls: 
            yield scrapy.Request(url=url, callback=self.handleProductDetails, dont_filter=True)

        # 商品列表下一页
        next = response.css(self.config['listNextSelector']).extract_first()
        if next is not None:
            yield scrapy.Request(url=next, callback=self.handleProductList, dont_filter=True)

    
    # 处理商品详情
    def handleProductDetails(self, response):
        item = ProductItem()
        # 根据面包屑获取分类等级数组
        item['categories'] = response.css(self.config['breadcrumbSelector']).extract()[1:]  
        # 爬取的价格去掉 $        
        item['products_price'] = response.css(self.config['productsPriceSelector']).extract_first().replace('$','').replace(' ','')   
        # 爬取的名称作为文件名去掉 /
        item['products_name'] = response.css(self.config['productsNameSelector']).extract_first().replace('/','').replace('\\','')    
        item['products_description'] = response.css(self.config['productsDescriptionSelector']).extract_first()
        item['products_images'] = response.css(self.config['productsImagesSelector']).extract()
        yield item
