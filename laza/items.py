# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LazaItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	# pass
	title = scrapy.Field()
	link_produk = scrapy.Field()
	price = scrapy.Field()
	price_old = scrapy.Field()
	diskon = scrapy.Field()
	img=scrapy.Field()
	description=scrapy.Field()
	brand=scrapy.Field()