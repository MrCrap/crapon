# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class LazaItem(scrapy.Item):
	Title = scrapy.Field()
	ProductUrl = scrapy.Field()
	Price = scrapy.Field()
	OldPrice = scrapy.Field()
	Discount = scrapy.Field()
	Images = scrapy.Field()
	Description = scrapy.Field()
	Brand = scrapy.Field()