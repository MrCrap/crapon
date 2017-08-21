import os
import csv

import MySQLdb
import MySQLdb.cursors

dbhost='127.0.0.1'
dbuser='toro'
dbpass=''
dbname='ScrapyEcom'

def connect(curdict=None):
	if curdict:
		db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname, charset='utf8',use_unicode=True, cursorclass=MySQLdb.cursors.DictCursor)
		cursor = db.cursor()
	else:
		db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname, charset='utf8',use_unicode=True)
		cursor = db.cursor()
	return db, cursor

# cursor.execute('''SELECT Title FROM Items WHERE id=1''')
# hasil = cursor.fetchone()
# print 'hasil', hasil['Title']

'''
SAVING CSV TO DB
'''
# header CSV
# Domain,OldPrice,Description,Keyword,Title,Brand,Slug,Discount,ProductUrl,Tag,Spek,Images,ImagesPath,Summary,Price,SmallDesc
def main():
	db, cursor=connect(True)
	with open('Tablet.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			Domain = str(row[0])
			OldPrice = str(row[1])
			Description = str(row[2])
			Keyword = str(row[3])
			Title = str(row[4])
			Brand = str(row[5])
			Slug = str(row[6])
			Discount = str(row[7])
			ProductUrl = str(row[8])
			Tag = str(row[9])
			Spek = str(row[10])
			Images = str(row[11])
			ImagesPath = str(row[12])
			Summary = str(row[13])
			Price = str(row[14])
			SmallDesc = str(row[15])
			cursor.execute('''SELECT id FROM Items WHERE ProductUrl=%s ''', (ProductUrl, ))
			ada = cursor.fetchone()
			if not ada:
				# CEK BRAND
				cursor.execute('''SELECT id FROM Brands WHERE name=%s ''', (Brand,))
				resBrand = cursor.fetchone()
				if not resBrand:
					slug = str(Brand).lower().replace(' ', '-')
					cursor.execute('''INSERT INTO Brands(name, slug)VALUES(%s,%s)''',(Brand, slug))
					db.commit()
					brand_id = cursor.lastrowid
				else:
					brand_id = resBrand['id']

				cursor.execute("""SET NAMES 'utf8mb4';""")
				cursor.execute('''
					INSERT INTO Items(Domain,OldPrice,Description,Keyword,Title,Brand,Slug,Discount,ProductUrl,Tag,Spek,Images,ImagesPath,Summary,Price,SmallDesc)
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
					''', (
						Domain,OldPrice,Description,Keyword,Title,brand_id,Slug,Discount,ProductUrl,Tag,Spek,Images,ImagesPath,Summary,Price,SmallDesc
					)
				)
				db.commit()
				post_id = cursor.lastrowid

				cursor.execute('''INSERT INTO PostRelated(post_id, cat_id, brand_id)VALUES(%s,%s,%s)'''%(post_id, 2, brand_id))
				db.commit()

	db.close()

def cats():
	# reset Brands
	db, cursor=connect(True)
	ListBrands = ['Samsung','Xiaomi','OPPO','Vivo','ASUS','Apple','Lenovo','Sony','Nokia','Huawei','Advan','Evercoss','SMARTFREN','LG','Polytron','Coolpad','Mito','BlackBerry','Acer','HTC','ZTE','Motorola','Axioo','Meizu','Himax','Alcatel','StrawBerry','Aldo','Microsoft','Asiafone','Infinix','Wiko','MAXTRON','Lava','Honor','Hisense','Nexian','SPC mobile','Blackview','Google','Kata','nubia','Cross Mobile','IMO','Sharp','OnePlus','iCherry iCherry','Pixcom','VENERA','CSL Mobile','HP','Gionee','Zyrex','TREQ','BEYOND','Cyrus','Movi','vernee','O2','HT mobile','ThL','SUNBERRY','LeEco','TiPhone','GOSCO','Blaupunkt','LUNA','VITELL','Philips','DOOGEE','K-TOUCH','AccessGo','XP MOBILE','KENXINDA','Skycall','MICXON','i-mobile','Bolt','Elephone','Dell','Ivio','Nextbit','DGTel','Haier','Garmin-Asus','Dopod','TAXCO mobile','YotaPhone','Essential','NEXCOM','ARCHOS','Titan','Amazon','D-ONE','Panasonic','Lexus Mobile','IT MOBILE','CAT','GSTAR','Sonim','Meitu','BenQ','Kodak','GT MOBILE','RedBerry','SPEEDUP','Kyocera','Olive','OSMO','Konka','TOM Mobile','Virtu-v','Audiovox','Blu','Dezzo Mobile','GIGABYTE','Tabulet','ZOPO ZOPO','Komodo','Intex','Kozi','Adline Mobile']
	for x in ListBrands:
		slug = str(x).lower().replace(' ', '-')
		cursor.execute('''INSERT INTO Brands(name, slug)VALUES(%s,%s)''', (x, slug))
		db.commit()

	db.close()

if __name__ == "__main__":
	# cats()
	main()