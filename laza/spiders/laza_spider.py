# -*- coding: utf-8 -*-
__author__ = "MrCrap"
__copyright__ = "Copyright 2017, The Crapon Project"
__license__ = "GPL"
__email__ = "ari.prihantoro@gail.com"
__status__ = "Devel"
__version__ = "1.0"

# -*- coding: utf-8 -*-
from functools import wraps, partial
from urlparse import urlparse
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.python import get_func_args
from scrapy.selector import HtmlXPathSelector

from laza.items import LazaItem
import ast
import json
import locale

import sys
reload(sys)
sys.setdefaultencoding('utf8')

ListBrands = ['iphone', 'samsung', 'asus', 'xiaomi', 'oppo', 'vivo', 'lg', 'huawei', 'lenovo']
def valid_xml_char_ordinal(c):
	codepoint = ord(c)
	return (
		0x20 <= codepoint <= 0xD7FF or
		codepoint in (0x9, 0xA, 0xD) or
		0xE000 <= codepoint <= 0xFFFD or
		0x10000 <= codepoint <= 0x10FFFF
	)
def Currencer(Number, Preffix=False, Decimal=2):
	locale.setlocale(locale.LC_NUMERIC, 'IND')
	IDR = locale.format("%.*f", (Decimal, Number), True)
	if Preffix:
		return "Rp. {}".format(IDR)
	return IDR

class LazaSpider(scrapy.Spider):
	name = "laza"
	allowed_domains = [
		'www.lazada.co.id', 
		'www.mataharimall.com', 
		'www.jd.id'
	]

	start_urls = [
		'http://www.lazada.co.id/beli-handphone/samsung/?itemperpage=20', 
		'https://www.mataharimall.com/p-2/handphone?per_page=20',
		'https://www.jd.id/category/jual-smartphone-875061468.html'
		]
	rules = ( Rule(LinkExtractor(allow=(), restrict_css=('.c-paging__next-link', 'a.p-turn.p-next', '.c-pagination--next a')), callback="parse", follow=False),)

	def parse(self, response):
		domain = urlparse(response.url).netloc
		if domain == 'www.lazada.co.id':
			item_links = response.css('a.c-product-card__name ::attr(href)').extract()
			for a in item_links:
				yield scrapy.Request('http://www.lazada.co.id'+a, callback=self.Parsering, meta={'domain': domain})

			# Pagination Progress
			NEXT_PAGE_SELECTOR = '.c-paging__next-link ::attr(href)'
			next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
			if next_page:
				yield scrapy.Request(
					response.urljoin(next_page),
					callback=self.parse
				)

		elif domain == 'www.jd.id':
			item_links = response.css('.p-pic a ::attr(href)').extract()
			for a in item_links:
				links = 'https:'+str(a)
				yield scrapy.Request(links, callback=self.Parsering, meta={'domain': domain})

			# Pagination Progress
			NEXT_PAGE_SELECTOR = 'a.p-turn.p-next ::attr(href)'	
			next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
			if next_page:
				yield scrapy.Request(
					response.urljoin(next_page),
					callback=self.parse
				)

		else:
			# matahari
			item_links = response.css('a.c-card-product__link ::attr(href)').extract()
			for a in item_links:
				url_query = urlparse(a).query
				a = url_query.split('&')[2].replace('ct=', '').replace('https%3A%2F%2F', 'https://').replace('%2F', '/')
				yield scrapy.Request(a, callback=self.Parsering, meta={'domain': domain})

			# Pagination Progress
			NEXT_PAGE_SELECTOR = '.c-pagination--next a ::attr(href)'
			next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
			if next_page:
				yield scrapy.Request(
					response.urljoin(next_page),
					callback=self.parse
				)

	def Parsering(self, response):
		domain = response.meta.get('domain')
		if domain == 'www.lazada.co.id':
			title = response.xpath("//meta[@property='og:title']/@content").extract_first()
			if title:
				title = title.strip()

			price = response.css('span#special_price_box ::text').extract_first()
			img = response.css('.productImage ::attr(data-big)').extract_first()
			brand = response.css('.prod_header_brand_action a span ::text').extract_first()

			desc = response.css('#productDetails p').extract()
			desc = ''.join(desc).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')
			if not desc:
				desc = 'Harga {title}, spek {title}, masuk dalam kategori {cat}. Cek harga dan spek {title} terupdate setiap harinya'.format(title=title, cat=brand)

			try:
				discount = str(response.css('#product_saving_percentage ::text').extract_first())
				if discount == 'None':
					discount = '0'
			except:
				discount = '0'
			try:
				price_old = str(response.css('span.price_erase > #price_box ::text').extract_first())
			except:
				price_old = '0'

		elif domain == 'www.mataharimall.com':
			title = response.css('h1.c-product__name ::text').extract_first()
			if title:
				title = title.strip()

			price = response.css('.c-product__discount-price ::text').extract_first()
			if price:
				price = price.strip()

			img = response.css('a.cloud-zoom img::attr(src)').extract_first()
			brand = response.css('.c-recomendation-product__title h1::text').extract_first()
			if brand:
				brand = brand.replace('Produk Lainnya dari Smartphone', '')

			desc = response.css('#js-tab-descripsi-produk p').extract()
			desc = ''.join(desc).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')
			if not desc:
				desc = 'Harga {title}, spek {title}, masuk dalam kategori {cat}. Cek harga dan spek {title} terupdate setiap harinya'.format(title=title, cat=brand)

			try:
				discount = str(response.css('span.c-discount-label ::text').extract_first())
				if discount == 'None':
					discount = '0'
			except:
				discount = '0'
			try:
				price_old = str(response.css('.c-product__price ::text').extract_first())
			except:
				price_old = '0'

		else:
			# jd
			price_script = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
			json_script = json.loads(price_script)
			title = json_script['name']
			data_brand = [str(y) for y in ListBrands if y in title.lower().split(' ')]

			if data_brand:
				brand = data_brand[0]
			else:
				brand = 'Smartphone'
			try:
				price = json_script['offers']['lowPrice']
			except:
				price = response.css('.p-price span ::text').extract_first()

			if price:
				price = price.strip()

			img = 'https:'+json_script['image']
			desc = response.css('div.cnt p').extract()
			desc = ''.join(desc).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')
			if not desc:
				desc = 'Harga {title}, spek {title}, masuk dalam kategori {cat}. Cek harga dan spek {title} terupdate setiap harinya'.format(title=title, cat=brand)

			try:
				price_old = json_script['offers']['highPrice']
			except:
				price_old = '0'
			
			# RUMUS Currencer
			# pengurangan = hargaBesar - HargaMurah
			# diskon = pengurangan / hargaBesar * 100
			
			hargakurang = int(price_old) - int(price)
			harga_diskon = int(hargakurang)/int(price_old) * 100
			discount = harga_diskon

		price = str(price).lower().replace('rp ', '').replace('.', '').replace(',', '')
		price_old = str(price_old).lower().replace('rp ', '').replace('.', '').replace(',', '')
		
		data = dict(
			title = title.encode('utf-8'),
			price = price,
			price_old = price_old,
			discount = discount,
			produkUrl = response.url,
			img = img,
			brand = brand, 
			desc=desc.encode('utf-8')
		)

		return self.Iteming(data)

	def Paginations(self, domain):
		print 'domain == pagination ==== > ;', domain

		if domain == 'www.lazada.co.id':
			NEXT_PAGE_SELECTOR = '.c-paging__next-link ::attr(href)'
		elif domain == 'www.jd.id':
			NEXT_PAGE_SELECTOR = 'a.p-turn.p-next ::attr(href)'
		else:
			NEXT_PAGE_SELECTOR = '.c-pagination--next a::attr(href)'
		
		NEXT_PAGE_SELECTOR = 'a.p-turn.p-next ::attr(href)'	
		next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
		if next_page:
			yield scrapy.Request(
				response.urljoin(next_page),
				callback=self.parse
			)

	def Iteming(self, data):
		item = None
		if data:
			item = LazaItem()
			item['Title'] = data['title']
			item['ProductUrl'] = data['produkUrl']
			item['Price'] = data['price']
			item['OldPrice'] = data['price_old']
			item['Discount'] = data['discount']
			item['Images'] = data['img']
			item['Brand'] = data['brand']
			item['Description']= data['desc']

		yield item
