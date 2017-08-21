import MySQLdb
import MySQLdb.cursors

#dbhost='23.95.56.154'
#dbuser='root'
#dbpass='berkahanak2016'
dbhost='198.12.64.10'
dbuser='toro'
dbpass='1234lima'
dbname='themeforest'

def connect(curdict=None):
	if curdict:
		db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname, charset='utf8',use_unicode=True, cursorclass=MySQLdb.cursors.DictCursor)
		cursor = db.cursor()
	else:
		db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname, charset='utf8',use_unicode=True)
		cursor = db.cursor()
	return db, cursor
