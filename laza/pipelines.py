# -*- coding: utf-8 -*-
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
 
settings = get_project_settings()

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class LazaPipeline(object):
	def process_item(self, item, spider):
		return item


class JsonPipeline(object):
	def __init__(self):
		self.file = open("Result.json", 'wb')
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
		self.file = open("Result.csv", 'wb')
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
	insert_sql = """INSERT INTO testtings (%s) VALUES ( %s )"""    
 
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