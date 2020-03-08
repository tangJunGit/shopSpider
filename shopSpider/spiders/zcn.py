# -*- coding: utf-8 -*-
import scrapy
from shopSpider.items import ProductItem
import json

class ZcnSpider(scrapy.Spider):
    name = 'zcn'
    allowed_domains = ['janefinds.com']
    start_urls = ['https://janefinds.com/']
    api = 'https://janefinds.com'

    # ========= 自定义配置项 =============
    config = {
        ### ==========   菜单导航条
        # 一级菜单导航通过index过滤
        'mainNavBarFilterByIndex': [],          
        # 一级菜单导航选择器          
        'mainNavBarSelector': '.site-nav-dropdown .style_2 .inner',
        # 一级菜单导航选择器的链接获取
        'mainNavBarLink':'a::attr(href)',       

        ### ==========    商品列表
        # 商品列表链接选择器
        'listUrlsSelector': '.products-grid .product-title::attr("href")',     
        # 商品列表下一页按钮选择器
        'listNextSelector': '.next-page>a::attr("href")',         

        ### ==========    商品分类
        # 商品分类选择器
        'breadcrumbSelector': '.breadcrumb>a::text',           

        ### ==========    商品详情
        # 商品价格选择器
        'productsPriceSelector': '#add-to-cart-form .prices>.price::text',          
        # 商品名称选择器                        
        'productsNameSelector': '.product-shop>.product-title>h2>span::text',        
        # 商品描述选择器         
        'productsDescriptionSelector': '.short-description',       
        # 商品图片选择器    
        'productsImagesSelector': 'a::attr("data-image")', 
    }

    def parse(self, response):
        # 获取分类链接
        category_urls = self.getCategoryUrls(response)   
        method = 2
        
        # 根据商品分类请求商品列表页面
        if(method == 1):
            for url in category_urls:
                yield scrapy.Request(url=url, callback=self.handleProductList, dont_filter=True)

        
        # 根据商品分类请求商品列表接口
        if(method == 2):
            for url in category_urls:
                # 第一页接口处理
                path = '{0}{1}?view=lsa&page=1'.format(self.api, url)
                yield scrapy.Request(url=path, callback=self.handleProductListApi, dont_filter=True, meta={'page': 1, 'url': url})

        

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
            hrefs = navBar.css(self.config['mainNavBarLink']).extract()
            category_urls.extend(hrefs)
        
        return category_urls


    # 处理商品列表页面
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


    # 处理商品列表接口
    def handleProductListApi(self, response):
        productList = json.loads(response.body)
        if(len(productList) == 0):
            return

        meta = response.meta
        page = meta['page'] + 1
        url = meta['url']

        # 请求商品详情
        for product in productList:
            yield scrapy.Request(url=self.api + product['url'], callback=self.handleProductDetails, dont_filter=True)
        
        # 接口处理
        path = '{0}{1}?view=lsa&page={2}'.format(self.api, url, page)
        yield scrapy.Request(url=path, callback=self.handleProductListApi, dont_filter=True, meta={'page': page, 'url': url})
    
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
