# -*- coding: utf-8 -*-
import scrapy
from scrapy.pipelines.images import ImagesPipeline, ImageException
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings

import MySQLdb
settings = get_project_settings()

# MongoEngine
from mongoengine import *

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
class LazaPipeline(object):
	def process_item(self, item, spider):
		return item

class MyImagesPipeline(ImagesPipeline):
	def get_media_requests(self, item, info):
		for image_url in item['Images']:
			yield scrapy.Request(image_url)

	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		if not image_paths:
			raise DropItem("Item contains no images")
		
		item['ImagesPath'] = image_paths

		return item

class MongoDBEnginePipeline(object):
	def process_item(self, item, spider):
		connect('laza')

		# # Query search_text order by text_scored
		# cek = [x.Title for x in PostProduk.objects.search_text('xiaomi').order_by('$text_score')]

		ceker = [x.Slug for x in PostProduk.objects(Slug=item['Slug']) if x.Slug == item['Slug']]
		post = PostProduk(
			Title=item['Title'],
			Brand = item['Brand'],
			ProductUrl = item['ProductUrl'],
			Price = item['Price'],
			OldPrice = item['OldPrice'],
			Discount = item['Discount'],
			Images = item['Images'],
			Description = item['Description'],
			Summary = item['Summary'],
			Slug = item['Slug'],
			Keyword = item['Keyword'],
			Tag = item['Tag'],
			Domain = item['Domain'],
			Spek = item['Spek'],
			ImagesPath = item['ImagesPath'],
			Category = item['Category']
		)
		if not ceker:
			post.save()


		return item

class PostProduk(Document):
	Title = StringField()
	ProductUrl = StringField(required=True)
	Price = StringField(max_length=100)
	OldPrice = StringField(max_length=50)
	Discount = StringField(max_length=100)
	Images = ListField(StringField())
	Description = StringField()
	Brand = StringField(max_length=50)
	Summary = StringField()
	Slug = StringField()
	Keyword = StringField()
	Tag = StringField()
	Domain = StringField(max_length=50)
	Spek = StringField()
	ImagesPath = ListField(StringField())
	Category = StringField(max_length=50)
	meta = {
        'indexes': [
            'Title',
            '$Title',  # text index
            '#Title',  # hashed index
            ('Title', '-Title')
        ]
    }


class JsonPipeline(object):
	def __init__(self):
		self.file = open("Lazadah.json", 'wb')
		self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
		self.exporter.start_exporting()
 
	def close_spider(self, spider):
		self.exporter.finish_exporting()
		self.file.close()
 
	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item

class CsvPipeline(object):
	def __init__(self):
		self.file = open("Tablet.csv", 'wb')
		self.exporter = CsvItemExporter(self.file, unicode)
		self.exporter.start_exporting()
 
	def close_spider(self, spider):
		self.exporter.finish_exporting()
		self.file.close()
 
	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item

class FundPipeline(object):
	# The table you items.FundItem class map to, my table is named fund    
	insert_sql = """INSERT INTO Items(%s)VALUES(%s)"""
 
	def __init__(self):    
		dbargs = settings.get('DB_CONNECT')
		db_server = settings.get('DB_SERVER')
		dbpool = adbapi.ConnectionPool(db_server, **dbargs)    
		self.dbpool = dbpool
 
	def __del__(self):    
		self.dbpool.close()
 
	def process_item(self, item, spider):
		self.insert_data(item, self.insert_sql)
		return item    
 
	def insert_data(self, item, insert):
		keys = item.keys()
		fields = u','.join(keys)
		qm = u','.join([u'%s'] * len(keys))
		sql = insert % (fields, qm)
		data = [item[k] for k in keys]

		return self.dbpool.runOperation(sql, data)

class MySQLStorePipeline(object):
	def __init__(self):
		self.conn = MySQLdb.connect('127.0.0.1', 'toro', '', 'ScrapyEcom', charset="utf8", use_unicode=True)
		self.cursor = self.conn.cursor()

	def process_item(self, item, spider):
		self.cursor.execute('''SELECT id FROM Items WHERE ProductUrl="%s" OR Slug="%s" '''%(item['ProductUrl'],item['Slug']))
		hasil = self.cursor.fetchall()
		if not hasil:
			# Get Brand_id From Brands
			self.cursor.execute('''SELECT id FROM Brands WHERE name=%s''', (item['Brand'],))
			res = self.cursor.fetchone()
			if not res:
				brand = item['Brand']
				slug = str(brand).lower().replace(' ', '-')
				self.cursor.execute('''INSERT INTO Brands(name,slug)VALUES(%s,%s)''', (item['Brand'], slug))
				self.conn.commit()
				brand_id = self.cursor.lastrowid
			else:
				brand_id = res[0]

			# Saving Items to DB
			image_url = ','.join(item['Images'])
			image_path = ','.join(item['ImagesPath'])
			insert_sql = """SET NAMES 'utf8mb4';"""
			self.cursor.execute(insert_sql)
			self.cursor.execute(
				"""INSERT INTO Items(Images,Title,Brand,ProductUrl,OldPrice,Price,Discount,Description,Summary,Slug,Keyword,Tag,Domain,Spek, ImagesPath,SmallDesc) 
					VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
				""", (image_url, item['Title'], brand_id, item['ProductUrl'], item['OldPrice'], item['Price'],item['Discount'], item['Description'], item['Summary'], item['Slug'], item['Keyword'], item['Tag'], item['Domain'], item['Spek'],image_path, item['SmallDesc'] ))
			self.conn.commit()
			post_id = self.cursor.lastrowid

			self.cursor.execute('''INSERT INTO PostRelated(post_id, cat_id, brand_id)VALUES(%s,%s,%s)'''%(post_id, 1, brand_id))
			self.conn.commit()

		# self.conn.close()

		return item

		