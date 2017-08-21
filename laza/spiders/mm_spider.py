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
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from laza.items import LazaItem
import ast
import simplejson
import locale
import sys, json

from slugify import slugify
# from libraries.sum.main import SummaryTool


from mongoengine import *

reload(sys)
sys.setdefaultencoding('utf8')

ListBrands = ['Samsung','Xiaomi','OPPO','Vivo','ASUS','Apple','Lenovo','Sony','Nokia','Huawei','Advan','Evercoss Evercoss','SMARTFREN','LG','Polytron','Coolpad','Mito','BlackBerry','Acer','HTC','ZTE','Motorola','Axioo','Meizu','Himax','Alcatel','StrawBerry','Aldo','Microsoft','Asiafone','Infinix','Wiko','MAXTRON','Lava','Honor','Hisense','Nexian','SPC mobile','Blackview','Google','Kata','nubia','Cross Mobile','IMO','Sharp','OnePlus','iCherry iCherry','Pixcom','VENERA','CSL Mobile','HP','Gionee','Zyrex','TREQ','BEYOND','Cyrus','Movi','vernee','O2','HT mobile','ThL','SUNBERRY','LeEco','TiPhone','GOSCO','Blaupunkt','LUNA','VITELL','Philips','DOOGEE','K-TOUCH','AccessGo','XP MOBILE','KENXINDA','Skycall','MICXON','i-mobile','Bolt','Elephone','Dell','Ivio','Nextbit','DGTel','Haier','Garmin-Asus','Dopod','TAXCO mobile','YotaPhone','Essential','NEXCOM','ARCHOS','Titan','Amazon','D-ONE','Panasonic','Lexus Mobile','IT MOBILE','CAT','GSTAR','Sonim','Meitu','BenQ','Kodak','GT MOBILE','RedBerry','SPEEDUP','Kyocera','Olive','OSMO','Konka','TOM Mobile','Virtu-v','Audiovox','Blu','Dezzo Mobile','GIGABYTE','Tabulet','ZOPO ZOPO','Komodo','Intex','Kozi','Adline Mobile']

def Currencer(Number, Preffix=False, Decimal=2):
	locale.setlocale(locale.LC_NUMERIC, 'IND')
	IDR = locale.format("%.*f", (Decimal, Number), True)
	if Preffix:
		return "Rp. {}".format(IDR)
	return IDR

class Sites(Document):
	_id = StringField()
	category = StringField()
	url = StringField()
	types = StringField()
		
class LazaSpider(scrapy.Spider):
	name = "mm"
	allowed_domains = [ 'www.mataharimall.com' ]

	start_urls = []
	rules = ( Rule(LinkExtractor(allow=()), callback="parse", follow=False), )

	def parse(self, response):
		item_links = response.css('a.c-card-product__link ::attr(href)').extract()
		for a in item_links:
			url_query = urlparse(a).query
			links = url_query.split('&')[2].replace('ct=', '').replace('https%3A%2F%2F', 'https://').replace('%2F', '/')
			yield scrapy.Request(links, callback=self.Parsering)

		# # Pagination Progress
		# next_page = response.css('.c-pagination--next a ::attr(href)').extract_first()
		# if next_page:
		# 	yield scrapy.Request(
		# 		response.urljoin(next_page),
		# 		callback=self.parse
		# 	)

	def start_requests(self):
		connect('laza')
		testing = Sites.objects(types='mm')
		for x in testing:
			yield self.make_requests_from_url(x['url'])
		connect().close()

	def Parsering(self, response):
 		cats = response.css('ul.c-breadcrumb__body li.c-breadcrumb__item a>span ::text').extract()
		category = cats[2]
		dataJsonGet = str(response.xpath('//script[@type="application/ld+json"]/text()').extract_first()).strip()
		DataJSON = json.loads(dataJsonGet)

		title = DataJSON['name']
		title = str(title).strip().replace('\n', ' ')

		price = DataJSON['offers']['price']
		img = str(DataJSON['image']).split()
		brand = DataJSON['brand']['name']
		desc = str(DataJSON['description']).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')

		spek = response.css('table.c-table-spec-products').extract_first()
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
		
		data = dict(
			title = title,
			price = price,
			price_old = price_old,
			discount = str(discount).strip(),
			produkUrl = response.url,
			img = img,
			brand = str(brand), 
			desc= str(desc),
			Summary = str(Summary).strip(),
			Slug = Slug,
			Keyword = Keyword,
			Tag = str(Tag),
			Domain = 'mataharimall.com',
			Spek = str(spek),
			SmallDesc = '',
			category=category
		)

		return self.Iteming(data)

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
			# item['ImagesPath'] = ''
			item['SmallDesc'] = data['SmallDesc']
			item['Category'] = data['category']
			
		yield item