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
	name = "laza"
	allowed_domains = [ 'www.lazada.co.id' ]
	custom_settings = {
        'LOG_FILE': 'error_LAZA.log',
        'LOG_LEVEL': 'ERROR'
    }

	start_urls = []
	rules = ( Rule(LinkExtractor(allow=()), callback="parse", follow=False), )

	def parse(self, response):
		item_links = response.css('a.c-product-card__name ::attr(href)').extract()
		for a in item_links:
			yield scrapy.Request('http://www.lazada.co.id'+a, callback=self.Parsering, meta={'domain': 'lazada.co.id'})

		# Pagination Progress
		next_page = response.css('.c-paging__next-link ::attr(href)').extract_first()
		if next_page:
			yield scrapy.Request(
				response.urljoin(next_page),
				callback=self.parse
			)

	def start_requests(self):
		connect('laza')
		testing = Sites.objects(types='laza').limit(1)
		for x in testing:
			yield self.make_requests_from_url(x['url'])


	def Parsering(self, response):
		dataJsonGet = str(response.xpath('//script[@type="application/ld+json"]/text()').extract_first()).strip()

		DataJSON = json.loads(dataJsonGet)
		list_cat = DataJSON['category']

		re_cat = list_cat.replace(' > ', ',')
		category = re_cat.split(',')
		
		domain = response.meta.get('domain')
		title = DataJSON['name']
		if title:
			title = str(title).strip().replace('\n', ' ')
		try:
			price = response.css('span#special_price_box ::text').extract_first()
			price = str(price).lower().replace('rp ', '').replace('.', '').replace(',', '').strip()
		except:
			price = '0'

		if not price or price == '0' :
			try:
				price = DataJSON['price']
			except:
				price = DataJSON['offers']['lowPrice']
			
			

		img = response.css('div.prd-moreImagesListContainer ul li div.lfloat.ui-border .productImage ::attr(data-big)').extract()
		img = [str(x) for x in img if x]
		
		brand = DataJSON['brand']['name']
		
		Slug = slugify(title)
		Tag = Slug.replace('-', ',').lower()

		try:
			Summary = response.xpath("//meta[@property='og:description']/@content").extract_first()
		except:
			Summary = response.xpath("//meta[@name='description']/@content").extract_first()
		
		Keyword = Slug.replace('-', ',')
		Keyword = Keyword+',bandingkan,harga,spek,murah'

		desc = DataJSON['description']
		small_desc = 'Harga {title}, spek {title}, masuk dalam kategori {cat}. Cek harga dan spek {title} terupdate setiap harinya'.format(title=title, cat=brand)
		short_desc_ul = response.css('ul.prd-attributesList').extract_first()
		
		spek = response.css('table.specification-table').extract_first()
		spek = spek.strip().replace('\n', '').replace('                        ', '').replace('        ', '').replace('            ', '')
		spek = spek.replace('                                                                                                    ','')

		try:
			discount = str(response.css('#product_saving_percentage ::text').extract_first())
			if discount == 'None':
				discount = '0'
		except:
			discount = '0'
		try:
			price_old = DataJSON['offers']['highPrice']
		except:
			price_old = str(response.css('span.price_erase > #price_box ::text').extract_first())
		else:
			price_old = '0'

		price_old = str(price_old).lower().replace('rp ', '').replace('.', '').replace(',', '').strip()
		try:
			ratVal = DataJSON['aggregateRating']['ratingValue']
			ratVal = int(round(ratVal*20))
			ratVal = str(ratVal)
			RatingCount = DataJSON['aggregateRating']['ratingCount']
		except:
			ratVal = '0'
			RatingCount = '0'

		try:
			reviews = DataJSON['review']
		except:
			reviews = []

		garansi = response.css('.warranty-info__message ::text').extract_first()

		data = dict(
			title = title,
			price = str(price),
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
			Domain = domain,
			Spek = str(spek),
			SmallDesc = small_desc,
			category=category,
			reviews = reviews,
			sku = DataJSON['sku'],
			ratingValue = str(ratVal),
			ratingCount = str(RatingCount),
			short_desc_ul=short_desc_ul,
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
			item['Reviews'] = data['reviews']
			item['SKU'] = data['sku']
			item['RatingValue'] = data['ratingValue']
			item['RatingCount'] = data['ratingCount']
			item['ShortDesc'] = data['short_desc_ul']
			item['Garansi'] = data['garansi']
			item['AffLink'] = ''
			
		yield item
