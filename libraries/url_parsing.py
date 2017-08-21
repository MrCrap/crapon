# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re

PROTOCOLS = [u'ed2k', u'ftp', u'http', u'https', u'irc', u'mailto', u'news', u'gopher', u'nntp', u'telnet', u'webcal',
			 u'xmpp', u'callto', u'feed', u'urn', u'aim', u'rsync', u'tag', u'ssh', u'sftp', u'rtsp', u'afs']

TLDS = """ac ad ae aero af ag ai al am an ao aq ar arpa as asia at au aw ax az
	   ba bb bd be bf bg bh bi biz bj bm bn bo br bs bt bv bw by bz ca cat
	   cc cd cf cg ch ci ck cl cm cn co com coop cr cu cv cx cy cz de dj dk
	   dm do dz ec edu ee eg er es et eu fi fj fk fm fo fr ga gb gd ge gf gg
	   gh gi gl gm gn gov gp gq gr gs gt gu gw gy hk hm hn hr ht hu id ie il
	   im in info int io iq ir is it je jm jo jobs jp ke kg kh ki km kn kp
	   kr kw ky kz la lb lc li lk lr ls lt lu lv ly ma mc md me mg mh mil mk
	   ml mm mn mo mobi mp mq mr ms mt mu museum mv mw mx my mz na name nc ne
	   net nf ng ni nl no np nr nu nz om org pa pe pf pg ph pk pl pm pn pr pro
	   ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sj sk sl sm sn so
	   sr st su sv sy sz tc td tel tf tg th tj tk tl tm tn to tp tr travel tt
	   tv tw tz ua ug uk us uy uz va vc ve vg vi vn vu wf ws xn ye yt yu za zm
	   zw academy accountant accountants actor adult agency airforce apartments archi army
	   associates attorney auction audio band bar bargains bayern beer berlin
	   best bid bike bingo bio black blackfriday blue boutique brussels
	   build builders business buzz cab cafe camera camp capetown capital
	   cards care career careers casa cash casino catering center ceo
	   chat cheap christmas church city claims cleaning click clinic clothing
	   club coach codes coffee cologne community company computer condos construction
	   consulting contractors cooking cool country coupons credit cricket cruises dance
	   date dating deals degree delivery democrat dental dentist desi design
	   diamonds diet digital direct directory discount dog domains download durban
	   education email energy engineer engineering enterprises equipment estate events exchange
	   expert exposed express fail faith farm fashion finance financial fish
	   fishing fit fitness flights florist flowers football forsale foundation fund
	   furniture futbol gallery garden gift gifts gives glass global gold
	   golf graphics gratis green gripe guide guitars guru hamburg haus
	   healthcare help hiphop hiv hockey holdings holiday horse host hosting
	   house how immo immobilien industries ink institute insure international investments
	   jetzt jewelry joburg juegos kaufen kim kitchen kiwi koeln land
	   lawyer lease legal lgbt life lighting limited limo link loan
	   loans lol london love ltda luxury maison management market marketing
	   media melbourne memorial menu moda moe money mortgage nagoya navy
	   network news ngo ninja nrw nyc nz okinawa onl online
	   osaka paris partners parts party photo photography photos physio pics
	   pictures pink pizza place plumbing plus poker porn press productions
	   properties property pub qpon quebec racing recipes red rehab reise
	   reisen rentals repair report republican rest restaurant review reviews rich
	   rip rocks rodeo ruhr run ryukyu saarland sale sarl school
	   schule science scot services sexy shiksha shoes show singles site
	   soccer social software solar solutions soy space style supplies supply
	   support surf surgery sydney systems tattoo tax taxi team tech
	   technology tennis theater tienda tips tires today tokyo tools top
	   tours town toys trade training university uno vacations vegas ventures versicherung
	   vet viajes video villas vision vlaanderen vodka vote voting voto
	   voyage wang watch webcam website wed wedding whoswho wien wiki win
	   work works world wtf орг xyz yoga yokohama zone""".split()

punct_re = re.compile(r'([\.,]+)$')

proto_re = re.compile(r'^[\w-]+:/{0,3}', re.IGNORECASE)

join_PROTOCOLS = '|'.join(PROTOCOLS)

#_urlfinderregex = re.compile(r'([^\s.\s]+\.[^\.\s]*)')
_urlfinderregex = re.compile(
	r"""\(*  # Match any opening parentheses.
	\b(?<![@.])(?:(?:{0}):/{{0,3}}(?:(?:\w+:)?\w+@)?)?  # http://
	(([\w-]+\.)+(?:{1})|[0-9]+(?:\.[0-9]+){{3}}(:[0-9]+)?)(?:\:\d+)?(?!\.\w)\b   # xx.yy.tld(:##)?
	(?:[/?][^\s\{{\}}\|\\\^\[\]`<>"]*)?
		# /path/zz (excluding "unsafe" chars from RFC 1738,
		# except for # and ~, which happen in practice)
	""".format(join_PROTOCOLS, '|'.join(TLDS)),
	re.IGNORECASE | re.VERBOSE | re.UNICODE)

#_urlfinderregex = re.compile(r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?")
class linkconvert:
	def __init__(self, text):
		self.link_index = -1
		self.links = []
		self.count_url = 0
		try:
			text = text.replace("\xc2", ' ').replace("\xa0", " ")
		except Exception, err:
			#open("error_link.log","a").write(str(err)+"\n"+str(text)+"\n")
			pass
		
		self.text = text
		
	def run(self):
		links = self.links
		findregex = _urlfinderregex.sub(self.replacewith, self.text)
		
		return links,findregex

	def handle_bracket(self, url):
		# huruf paling awal adalah (
		sebelum_url = "("
		url = url[1:]

		split_tutup_kurung = url.split(")")
		extract_url = split_tutup_kurung[0]

		if ")" in url:
			if len(split_tutup_kurung) > 1 and split_tutup_kurung[1]:
				setelah_url = ")"+")".join(url.split(")")[1:])
			else:
				setelah_url = ")"
		else:
			setelah_url = ""


		return extract_url, sebelum_url, setelah_url
	
	def replacewith(self, match):
		url = match.group(0)

		if url.startswith('('):
			_wrapping = self.handle_bracket(url)
			url, sebelum_url, setelah_url = _wrapping

		else:
			sebelum_url = setelah_url = ""

		m = re.search(punct_re, url)
		if m:
			url = url[0:m.start()]

		if 'themeforest.net' in str(url):
			url = str(url).replace("'", "")
			url = str(url).replace(url, str(url)+"?ref=mildtheme'")

		if 'photodune.net' in str(url):
			url = str(url).replace("'", "")
			url = str(url).replace(url, str(url)+"?ref=mildtheme'")

		if 'codecanyon.net' in str(url):
			url = str(url).replace("'", "")
			url = str(url).replace(url, str(url)+"?ref=mildtheme'")

		if 'videohive.net' in str(url):
			url = str(url).replace("'", "")
			url = str(url).replace(url, str(url)+"?ref=mildtheme'")

		_text = url
		repl = url
		

		self.links.append(_text)
		self.count_url += 1
		
		return repl
