# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import pymysql
import time

# 处理图片的文件路径
def haddleFileUrl(products_name, image_url):
    file_name = image_url.split('/')[-1]
    return u"{0}/{1}".format(products_name, file_name)

# 商品图片保存到本地
class ImagePipeline(ImagesPipeline):
    # 处理图片文件名
    def file_path(self, request, response=None, info=None):
        url = request.url
        products_name = request.meta['item']['products_name']
        return haddleFileUrl(products_name, url)
    
    # 图片下载异常处理
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        return item
    
    def get_media_requests(self, item, info):
        for url in item['products_images']: 
            yield Request(url=url, meta={'item':item})


# 商品信息保存到数据库
class MysqlPipeline():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    def __init__(self, host, database, user, password, port, images_store):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.images_store = images_store
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
            images_store=crawler.settings.get('IMAGES_STORE'),
        )
    
    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()
    
    def close_spider(self, spider):
        self.db.close()
    
    def process_item(self, item, spider):
        parent_id = 0     
        # 处理商品分类 
        for category_name in item['categories']:
            parent_id = self.productsCategoryStore(category_name, parent_id)

        # 处理商品详情
        self.productsDetailStore(item, parent_id)

            
    # 商品分类存储数据库
    def productsCategoryStore(self, category_name, parent_id):
        # 查询该分类id
        query_sql = 'SELECT categories_id FROM categories_description WHERE categories_name = (% s)'
        self.cursor.execute(query_sql, [category_name])
        category_id = self.cursor.fetchone()
        
        # 判断该分类是否存在
        if category_id is None:
            # 插入分类关联表
            insert_sql = 'INSERT INTO categories (parent_id, date_added, last_modified) VALUES (% s, % s, % s)'
            self.cursor.execute(insert_sql, [parent_id, self.current_time, self.current_time])
            category_id = self.cursor.lastrowid
            self.db.commit()

            # 插入分类详情表
            insert_sql = 'INSERT INTO categories_description (categories_id, categories_name, categories_description) VALUES (% s, % s, % s)'
            self.cursor.execute(insert_sql, [category_id, category_name, category_name])
            self.db.commit()

        return category_id


    # 商品详情存储数据库
    def productsDetailStore(self, item, category_id):
        # 插入商品表
        image_url = self.images_store +'/'+haddleFileUrl(item['products_name'], item['products_images'][0])   # 图片存的路径与下载文件路径一致
        insert_sql = 'INSERT INTO products (products_quantity, products_image, products_price, products_date_added, products_last_modified, products_date_available, products_status) VALUES (% s, % s, % s, % s, % s, % s, % s)'
        self.cursor.execute(insert_sql, [10000, image_url, item['products_price'], self.current_time, self.current_time, self.current_time, 1])
        products_id = self.cursor.lastrowid
        self.db.commit()

        # 插入商品详情表
        if products_id is not None:
            insert_sql = 'INSERT INTO products_description (products_id, products_name, products_description) VALUES (% s, % s, % s)'
            self.cursor.execute(insert_sql, [products_id, item['products_name'], item['products_description']])
            self.db.commit()

            insert_sql = 'INSERT INTO products_to_categories (products_id, categories_id) VALUES (% s, % s)'
            self.cursor.execute(insert_sql, [products_id, category_id])
            self.db.commit()

        return products_id