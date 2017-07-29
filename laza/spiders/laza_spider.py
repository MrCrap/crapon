# -*- coding: utf-8 -*-
from functools import wraps, partial
from urlparse import urlparse
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.python import get_func_args

from laza.items import LazaItem
import ast
import json

import locale

def rupiah_format(angka, with_prefix=False, desimal=2):
	locale.setlocale(locale.LC_NUMERIC, 'IND')
	rupiah = locale.format("%.*f", (desimal, angka), True)
	if with_prefix:
		return "Rp. {}".format(rupiah)
	return rupiah

class LazaSpider(scrapy.Spider):
	name = "laza"
	allowed_domains = [
		'www.lazada.co.id', 
		'www.mataharimall.com', 
		'www.jd.id'
	]

	start_urls = [
		# 'http://www.lazada.co.id/beli-handphone/samsung/?itemperpage=120', 
		# 'https://www.mataharimall.com/p-2/handphone?per_page=120',
		'https://www.jd.id/category/jual-smartphone-875061468.html'
		]
	rules = ( Rule(LinkExtractor(allow=(), restrict_css=('.c-paging__next-link')), callback="parse", follow=False),)

	def parse(self, response):
		domain = urlparse(response.url).netloc
		if domain == 'www.lazada.co.id':
			item_links = response.css('a.c-product-card__name ::attr(href)').extract()
			# for a in item_links:
			# 	yield scrapy.Request('http://www.lazada.co.id'+a, callback=self.Parsering, meta={'domain': domain})

			# NEXT_PAGE_SELECTOR = '.c-paging__next-link ::attr(href)'
			# next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
			# if next_page:
			# 	yield scrapy.Request(
			# 		response.urljoin(next_page),
			# 		callback=self.parse
			# 	)

		elif domain == 'www.jd.id':
			item_links = response.css('.p-pic a ::attr(href)').extract()
			for a in item_links:
				links = 'https:'+str(a)
				yield scrapy.Request(links, callback=self.Parsering, meta={'domain': domain})

			# NEXT_PAGE_SELECTOR = '.c-pagination--next a::attr(href)'
			# next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
			# if next_page:
			# 	yield scrapy.Request(
			# 		response.urljoin(next_page),
			# 		callback=self.parse
			# 	)

		else:
			item_links = response.css('a.c-card-product__link ::attr(href)').extract()
			for a in item_links:
				url_query = urlparse(a).query
				a = url_query.split('&')[2].replace('ct=', '').replace('https%3A%2F%2F', 'https://').replace('%2F', '/')
				# yield scrapy.Request(a, callback=self.Parsering, meta={'domain': domain})

			# NEXT_PAGE_SELECTOR = '.c-pagination--next a::attr(href)'
			# next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
			# if next_page:
			# 	yield scrapy.Request(
			# 		response.urljoin(next_page),
			# 		callback=self.parse
			# 	)

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
				diskon = str(response.css('#product_saving_percentage ::text').extract_first())
				if diskon == 'None':
					diskon = '0'
			except:
				diskon = '0'
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
				diskon = str(response.css('span.c-discount-label ::text').extract_first())
				if diskon == 'None':
					diskon = '0'
			except:
				diskon = '0'
			try:
				price_old = str(response.css('.c-product__price ::text').extract_first())
			except:
				price_old = '0'

		else:
			price_script = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
			json_script = json.loads(price_script)

			title = json_script['name']
			
			list_brand = ['iphone', 'samsung', 'asus', 'xiaomi', 'oppo', 'vivo', 'lg', 'huawei', 'lenovo']
			data_brand = [str(y) for y in list_brand if y in title.lower().split(' ')]
			if data_brand:
				brand = data_brand[0]
			else:
				brand = 'Handphone'
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
				diskon = str(response.css('span.discount-rate ::text').extract_first())
				if diskon == 'None':
					diskon = '0'
			except:
				diskon = '0'
			try:
				price_old = json_script['offers']['highPrice']
			except:
				price_old = '0'

		data = dict(
			title = title,
			price = price,
			price_old = price_old,
			diskon = diskon,
			link_produk = response.url,
			img = img,
			brand = brand, 
			desc=desc
		)

		return self.Iteming(data)

	def Iteming(self, data):
		item = None
		if data:
			item = LazaItem()
			item['title'] = data['title']
			item['price'] = data['price']
			item['price_old'] = data['price_old']
			item['diskon'] = data['diskon']
			item['link_produk'] = data['link_produk']
			item['img'] = data['img']
			item['brand'] = data['brand']
			item['description']= data['desc']

		yield item