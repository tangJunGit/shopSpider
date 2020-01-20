# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    categories = scrapy.Field()                 # 分类等级数组
    products_price = scrapy.Field()             # 商品价格
    products_name = scrapy.Field()              # 商品名称
    products_description = scrapy.Field()       # 商品描述
    products_images = scrapy.Field()            # 商品图片路径

