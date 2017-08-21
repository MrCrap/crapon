from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

class MySpider1(scrapy.Spider):
	print '1'

class MySpider2(scrapy.Spider):
	print '2'

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
	yield runner.crawl(MySpider1)
	yield runner.crawl(MySpider2)
	reactor.stop()

crawl()
reactor.run()