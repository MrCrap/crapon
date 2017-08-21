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
import simplejson
import locale
import sys, json

reload(sys)
sys.setdefaultencoding('utf8')

ListBrands = ['iphone', 'samsung', 'asus', 'xiaomi', 'oppo', 'vivo', 'lg', 'huawei', 'lenovo']

def Currencer(Number, Preffix=False, Decimal=2):
	locale.setlocale(locale.LC_NUMERIC, 'IND')
	IDR = locale.format("%.*f", (Decimal, Number), True)
	if Preffix:
		return "Rp. {}".format(IDR)
	return IDR

class EcommerceSpider(scrapy.Spider):
	name = ""
	allowed_domains = [
		'www.mataharimall.com', 
		'www.jd.id',
		'www.blibli.com'
	]

	start_urls = [
		'https://www.mataharimall.com/p-2/handphone?per_page=120',
		'https://www.jd.id/category/jual-smartphone-875061468.html',
		'https://www.blibli.com/handphone/54593?c=HA-1000002&r=120',
	]

	rules = ( 
		Rule(LinkExtractor(
			allow=(), 
			restrict_css=(
				'a.p-turn.p-next', 
				'.c-pagination--next a', 
				'a.pagingButton.next-button ::attr(onclick)'
				)
			),
			callback="parse", 
			follow=False),
	)

	def parse(self, response):
		domain = urlparse(response.url).netloc
		if domain == 'www.jd.id':
			item_links = response.css('.p-pic a ::attr(href)').extract()
			for a in item_links:
				links = 'https:'+str(a)
				yield scrapy.Request(links, callback=self.Parsering, meta={'domain': domain})

			# Pagination Progress
			next_page = response.css('a.p-turn.p-next ::attr(href)').extract_first()
			if next_page:
				yield scrapy.Request(
					response.urljoin(next_page),
					callback=self.parse
				)
		elif domain == 'www.blibli.com':
			item_links = response.css('a.single-product ::attr(href)').extract()
			for a in item_links:
				yield scrapy.Request(a, callback=self.Parsering, meta={'domain': domain})

			# Pagination Progress
			next_page = response.css('a.pagingButton.next-button ::attr(onclick)').extract_first()
			perPage = next_page[-5:].replace(');', '')
			linkPageStart = 'https://www.blibli.com/handphone/54593?c=HA-1000002&r=120'
			param = '&i=%s'%(perPage)
			next_page = linkPageStart+param
			if next_page:
				yield scrapy.Request(
					response.urljoin(next_page),
					callback=self.parse
				)

		else:
			# MM
			item_links = response.css('a.c-card-product__link ::attr(href)').extract()
			for a in item_links:
				url_query = urlparse(a).query
				links = url_query.split('&')[2].replace('ct=', '').replace('https%3A%2F%2F', 'https://').replace('%2F', '/')
				yield scrapy.Request(links, callback=self.Parsering, meta={'domain': domain})

			# Pagination Progress
			next_page = response.css('.c-pagination--next a ::attr(href)').extract_first()
			if next_page:
				yield scrapy.Request(
					response.urljoin(next_page),
					callback=self.parse
				)

	def Parsering(self, response):
		domain = response.meta.get('domain')
		if domain == 'www.mataharimall.com':
			dataJsonGet = str(response.xpath('//script[@type="application/ld+json"]/text()').extract_first()).strip()
			DataJSON = json.loads(dataJsonGet)

			title = DataJSON['name']
			title = str(title).strip().replace('\n', ' ')

			price = DataJSON['offers']['price']
			img = DataJSON['image']
			brand = DataJSON['brand']['name']
			desc = str(DataJSON['description']).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')

			spek = response.css('table.specification-table').extract_first()
			spek = spek.strip().replace('\n', '').replace('                        ', '').replace('        ', '').replace('            ', '')
			spek = spek.replace('                                                                                                    ','')
			
			if price:
				price = str(price).strip()

			try:
				discount = response.css('span.c-discount-label ::text').extract_first()
				discount = str(discount)
				if discount == 'None':
					discount = '0'
			except:
				discount = '0'

			try:
				price_old = response.css('div.c-product__price ::text').extract_first()
				price_old = str(price_old)
			except:
				price_old = '0'

			Tag = brand
			SlugTitle = title.replace(' - ', ' ')
			SlugReplace = SlugTitle.replace('[', '').replace(']', '').replace('/ ', '').replace('/', '')
			Slug = SlugReplace.replace(' ', '-').lower()

			try:
				Summary = response.xpath("//meta[@property='og:description']/@content").extract_first()
			except:
				Summary = response.xpath("//meta[@name='description']/@content").extract_first()
			
			Keyword = Slug.replace('-', ',')
			Keyword = Keyword+',bandingkan,harga,spek,murah'

		elif domain == 'www.blibli.com':
			# Some data json from site is invalid, skip by scrapy
			dataJsonGet = str(response.xpath('//script[@type="application/ld+json"]/text()').extract_first()).strip()
			DataJSON = json.loads(dataJsonGet)

			title = DataJSON['name']
			title = str(title).strip().replace('\n', ' ')
			price = DataJSON['offers']['price']
			img = DataJSON['image']
			brand = DataJSON['brand']['name']
			desc = str(DataJSON['description']).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')

			spek = response.css('table.specification-table').extract_first()
			spek = spek.strip().replace('\n', '').replace('                        ', '').replace('        ', '').replace('            ', '')
			spek = spek.replace('                                                                                                    ','')
			
			price_old = 0
			discount = 0
			Tag = brand
			SlugTitle = title.replace(' - ', ' ')
			SlugReplace = SlugTitle.replace('[', '').replace(']', '').replace('/ ', '').replace('/', '')
			Slug = SlugReplace.replace(' ', '-').lower()

			try:
				Summary = response.xpath("//meta[@property='og:description']/@content").extract_first()
			except:
				Summary = response.xpath("//meta[@name='description']/@content").extract_first()
			
			Keyword = Slug.replace('-', ',')
			Keyword = Keyword+',bandingkan,harga,spek,murah'

		else:
			# JD
			price_script = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
			json_script = json.loads(price_script)
			title = json_script['name']
			title = str(title).strip().replace('\n', ' ')
			data_brand = [str(y) for y in ListBrands if y in title.lower().split(' ')]

			if data_brand:
				brand = data_brand[0]
			else:
				brand = 'Smartphone'
			try:
				price = int(json_script['offers']['lowPrice'])
			except:
				price = 0

			img = 'https:'+json_script['image']
			desc = response.css('div.cnt p').extract()
			desc = ''.join(desc).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')
			if not desc:
				desc = 'Harga {title}, spek {title}, masuk dalam kategori {cat}. Cek harga dan spek {title} terupdate setiap harinya'.format(title=title, cat=brand)

			spek = response.css('table.specification-table').extract_first()
			spek = spek.strip().replace('\n', '').replace('                        ', '').replace('        ', '').replace('            ', '')
			spek = spek.replace('                                                                                                    ','')

			try:
				price_old = int(json_script['offers']['highPrice'].strip())
			except:
				price_old = 0
			
			# Note Currencer
			# differentPrice = bigPrice - lowPrice
			# discount = differentPrice / bigPrice * 100
			if int(price_old) > 0:
				firstPrice = int(price_old)
			else:
				firstPrice = int(price)

			Tag = brand
			SlugTitle = title.replace(' - ', ' ')
			SlugReplace = SlugTitle.replace('[', '').replace(']', '').replace('/ ', '').replace('/', '')
			Slug = SlugReplace.replace(' ', '-').lower()

			try:
				Summary = response.xpath("//meta[@property='og:description']/@content").extract_first()
			except:
				Summary = response.xpath("//meta[@name='description']/@content").extract_first()
			
			Keyword = Slug.replace('-', ',')
			Keyword = Keyword+',bandingkan,harga,spek,murah'

			differentPrice = firstPrice - int(price)
			if int(differentPrice) > 0:
				discountPrice = (float(differentPrice) / float(firstPrice)) * 100
				discount = int(discountPrice)
			else:
				discount = 0

		price = str(price).lower().replace('rp ', '').replace('.', '').replace(',', '').strip()
		price_old = str(price_old).lower().replace('rp ', '').replace('.', '').replace(',', '').strip()
		
		data = dict(
			title = title,
			price = price,
			price_old = price_old,
			discount = str(discount).strip(),
			produkUrl = response.url,
			img = str(img),
			brand = str(brand), 
			desc= str(desc),
			Summary = str(Summary).strip(),
			Slug = Slug,
			Keyword = Keyword,
			Tag = str(Tag),
			Domain = domain,
			Spek = str(spek),
		)

		return self.Iteming(data)

	# def Paginations(self, domain):
	# 	if domain == 'www.lazada.co.id':
	# 		NEXT_PAGE_SELECTOR = '.c-paging__next-link ::attr(href)'

	# 	elif domain == 'www.jd.id':
	# 		NEXT_PAGE_SELECTOR = 'a.p-turn.p-next ::attr(href)'

	# 	else:
	# 		NEXT_PAGE_SELECTOR = '.c-pagination--next a::attr(href)'
		
	# 	NEXT_PAGE_SELECTOR = 'a.p-turn.p-next ::attr(href)'	
	# 	next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
	# 	if next_page:
	# 		yield scrapy.Request(
	# 			response.urljoin(next_page),
	# 			callback=self.parse
	# 		)

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
			item['Summary'] = data['Summary']
			item['Slug'] = data['Slug']
			item['Keyword'] = data['Keyword']
			item['Tag'] = data['Tag']
			item['Domain'] = data['Domain']
			item['Spek'] = data['Spek']
			item['ImagesPath'] = ''

		yield item