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
	name = "jd"
	allowed_domains = [ 'www.jd.id' ]
	custom_settings = {
        'LOG_FILE': 'error_jd.log',
        'LOG_LEVEL': 'ERROR'
    }

	start_urls = []
	rules = ( Rule(LinkExtractor(allow=()), callback="parse", follow=False), )

	def parse(self, response):
		item_links = response.css('.p-pic a ::attr(href)').extract()
		for a in item_links:
			links = 'https:'+str(a)
			yield scrapy.Request(links, callback=self.Parsering)

		# Pagination Progress
		next_page = response.css('.pagination > a.p-next.p-turn ::attr(href)').extract_first()
		if next_page:
			next_page = 'https:'+next_page
			yield scrapy.Request(
				response.urljoin(next_page),
				callback=self.parse
			)

	def start_requests(self):
		connect('laza')
		GetUrl = Sites.objects(types='jd')
		for x in GetUrl:
			yield self.make_requests_from_url(x['url'])


	def Parsering(self, response):
		price_script = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
		json_script = json.loads(price_script)
		title = json_script['name']
		# print 'title', title

		brand = response.xpath('//input[@id="productBrand-ga"]/@value').extract_first()
		if not brand:
			brand = ''

		try:
			price = int(json_script['offers']['lowPrice'])
		except:
			price = '0'

		img = json_script['image']
		img = img.split()

		try:
			price_old = int(json_script['offers']['highPrice'])
		except:
			price_old = '0'

		garansi_list = response.css('div.from > span.warrp ::text').extract()
		if garansi_list:
			garansi = garansi_list[1]
		else:
			garansi = ''
		
		# Note Currencer
		# differentPrice = bigPrice - lowPrice
		# discount = differentPrice / bigPrice * 100
		if int(price_old) > 0:
			firstPrice = int(price_old)
		else:
			firstPrice = int(price)

		differentPrice = firstPrice - int(price)
		if int(differentPrice) > 0:
			discountPrice = (float(differentPrice) / float(firstPrice)) * 100
			discount = int(discountPrice)
		else:
			discount = 0
		try:
			ratVal = json_script['aggregateRating']['ratingValue']
			ratVal = int(round(ratVal*20))
			ratVal = str(ratVal)
			RatingCount = json_script['aggregateRating']['ratingCount']
		except:
			ratVal = '0'
			RatingCount = '0'

		data = dict(
			title = title,
			produkUrl = response.url,
			price = str(price),
			price_old = str(price_old),
			discount = str(discount),
			img = img,
			brand = str(brand),
			sku = json_script['sku'],
			ratingValue = str(ratVal),
			ratingCount = str(RatingCount),
			garansi = garansi
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
			item['Description']= ''
			item['Summary'] = ''
			item['Slug'] = ''
			item['Keyword'] = ''
			item['Tag'] = ''
			item['Domain'] = 'jd.id'
			item['Spek'] = ''
			item['SmallDesc'] = ''
			item['Category'] = []
			item['Reviews'] = []
			item['SKU'] = data['sku']
			item['RatingValue'] = data['ratingValue']
			item['RatingCount'] = data['ratingCount']
			item['ShortDesc'] = ''
			item['Garansi'] = data['garansi']
			item['AffLink'] = ''
			
		yield item
