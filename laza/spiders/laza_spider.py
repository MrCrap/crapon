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
		
class LazaSpider(scrapy.Spider):
	name = "laza"
	allowed_domains = [ 'www.lazada.co.id' ]

	start_urls = []
	rules = ( Rule(LinkExtractor(allow=()), callback="parse", follow=False), )

	def parse(self, response):
		item_links = response.css('a.c-product-card__name ::attr(href)').extract()
		for a in item_links:
			yield scrapy.Request('http://www.lazada.co.id'+a, callback=self.Parsering, meta={'domain': 'lazada.co.id'})

		# Pagination Progress
		# next_page = response.css('.c-paging__next-link ::attr(href)').extract_first()
		# if next_page:
		# 	yield scrapy.Request(
		# 		response.urljoin(next_page),
		# 		callback=self.parse
		# 	)

	def start_requests(self):
		connect('laza')
		testing = Sites.objects()
		for x in testing:
			yield self.make_requests_from_url(x['url'])
		connect().close()

	def Parsering(self, response):
 		cats = response.css('ul.breadcrumb__list li.breadcrumb__item span.breadcrumb__item-text a>span ::text').extract()
		category = cats[1]
		domain = response.meta.get('domain')
		title = response.xpath("//meta[@property='og:title']/@content").extract_first()
		if title:
			title = str(title).strip().replace('\n', ' ')

		price = response.css('span#special_price_box ::text').extract_first()
		img = response.css('.productImage ::attr(data-big)').extract()
		img = [str(x) for x in img]
		brand = response.css('.prod_header_brand_action a span ::text').extract_first()
		
		Slug = slugify(title)
		Tag = Slug.replace('-', ',').lower()

		try:
			Summary = response.xpath("//meta[@property='og:description']/@content").extract_first()
		except:
			Summary = response.xpath("//meta[@name='description']/@content").extract_first()
		
		Keyword = Slug.replace('-', ',')
		Keyword = Keyword+',bandingkan,harga,spek,murah'

		desc = response.css('#productDetails p').extract()
		desc = ''.join(desc).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')
		if not desc:
			descSel = response.css('.product-description__block ::text').extract()
			desc = ''.join(descSel).strip().replace('\n', ' ').replace('  ', '').replace('                     ', '')

		if not desc:
			desc = 'Harga {title}, spek {title}, masuk dalam kategori {cat}. Cek harga dan spek {title} terupdate setiap harinya'.format(title=title, cat=brand)

		# Build the summary with the sentences dictionary
		# st = SummaryTool()
		# sentences_dic = st.get_senteces_ranks(desc)
		# summarys = st.get_summary(title, desc, sentences_dic)
		# small_desc = summarys.strip()
		small_desc = ''

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
			price_old = str(response.css('span.price_erase > #price_box ::text').extract_first())
		except:
			price_old = '0'

		price = str(price).lower().replace('rp ', '').replace('.', '').replace(',', '').strip()
		price_old = str(price_old).lower().replace('rp ', '').replace('.', '').replace(',', '').strip()
		
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
			Domain = domain,
			Spek = str(spek),
			SmallDesc = small_desc,
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




# class MySpider1(scrapy.Spider):
# 	print '1'
# 	name = 'spider1'

# class MySpider2(scrapy.Spider):
# 	print '2'
# 	name = 'spider1'

# configure_logging()
# runner = CrawlerRunner()

# @defer.inlineCallbacks
# def crawl():
# 	yield runner.crawl(MySpider1)
# 	yield runner.crawl(MySpider2)
# 	reactor.stop()

# crawl()
# reactor.run()