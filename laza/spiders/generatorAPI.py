# -*- coding: utf-8 -*-
__author__ = "MrCrap"
__copyright__ = "Copyright 2017, The Crapon Project"
__name__ = "API Generator Affiliate Code"
__license__ = "GPL"
__email__ = "ari.prihantoro@gail.com"
__status__ = "Devel"
__version__ = "1.0"

import requests

class Generates(object):
	def __init__(self, param, domain):
		self.param = param
		self.domain = domain
	
	def main(self):
		pass

	def APIS(self, url, types):
		if types == 'lazada':
			keys = '7d6698dbdae6c876aa4f1940e8f0275ef565b1211986c80c0b0b00cdb48ad123'
			NetworkId = 'lazada'
			offer_id = 281

		elif types == 'matahari'
			keys = '10741bb590c89a5320e455dbb2d49edcbc359b55fda2196388f09adb1a6edf30'
			NetworkId = 'mataharimall'
			offer_id = 17

		else:
			# blanja
			keys = '12a4a2dd4c8f31c4eb4f894e024781f3128f784db6cfdfe2db26fe0c79ea3b9a'
			NetworkId = 'blanjacom'
			offer_id = 29
		
		req = 'https://api.hasoffers.com/Apiv3/json?NetworkId={network}&Target=Affiliate_Offer&Method=generateTrackingLink&api_key={key}&offer_id={offer_id}&params[url]={linke}'.format(key=keys,linke=url, network=NetworkId, offer_id=offer_id)

		page = urllib2.urlopen(req)
		data_aff = page.read()
		dete = json.loads(data_aff)
		link_aff = dete['response']['data']['click_url']

		return link_aff


# http://invol.co/aff_m?offer_id=94&aff_id=10580&source=deeplink_generator&url=http%3A%2F%2Fwww.lazada.co.id%2F
# http://invol.co/aff_m?offer_id=401&aff_id=10580&source=deeplink_generator&url=https%3A%2F%2Fwww.blibli.com%2F
# http://invol.co/aff_m?offer_id=1170&aff_id=10580&source=deeplink_generator&url=http%3A%2F%2Fwww.blanja.com%2F