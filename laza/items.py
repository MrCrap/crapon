# -*- coding: utf-8 -*-

'''YA RAZZAQ ZULQUWATIL MATIN URZUKNI'''

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
	Summary = scrapy.Field()
	Slug = scrapy.Field()
	Keyword = scrapy.Field()
	Tag = scrapy.Field()
	Domain = scrapy.Field()
	Spek = scrapy.Field()
	ImagesPath = scrapy.Field()
	SmallDesc = scrapy.Field()
	Category = scrapy.Field()
	Reviews = scrapy.Field()
	SKU = scrapy.Field()
	RatingValue = scrapy.Field()
	RatingCount = scrapy.Field()
	ShortDesc = scrapy.Field()
	Garansi = scrapy.Field()
	AffLink = scrapy.Field()