from config import postgres_config as p
from Market import get_minute_close
import logging
import psycopg2
################
# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
################

#TODO: need a dictionary of all tables + columns?


def save_articles(articles):

	logger.debug("in save()")
	# first connect to db
	conn_string = "host='{}' dbname='{}' user='{}' password='{}'".format(p.get('host'),p.get('dbname'),p.get('user'),p.get('password'))
	logger.debug(conn_string)
	conn = None
	try:
		conn = psycopg2.connect(conn_string)		

	except (Exception, psycopg2.DatabaseError) as error:
			logger.debug(error)
	else:
		logger.debug("Successfully connected to db")

		# save all articles w/ current market price
		for article in articles:
			try:
				conn = psycopg2.connect(conn_string)		

				# upserting to avoid adding duplicate articles
				sql = "INSERT INTO article(url,text) VALUES(%s,%s) ON CONFLICT DO NOTHING"

				cur = conn.cursor()
				cur.execute(sql, (article.url,article.text,))

				conn.commit()
				cur.close()
			except (Exception, psycopg2.DatabaseError) as error:
				logger.debug(error)
			else:
				# Potentially misleading because we may have upserted
				logger.info("Successfully entered into db")

	finally:
		if conn is not None:
			conn.close()


def set_market_price():
	logger.debug("in set_market_price")

	conn_string = "host='{}' dbname='{}' user='{}' password='{}'".format(p.get('host'),p.get('dbname'),p.get('user'),p.get('password'))
	logger.debug(conn_string)
	conn = None

	try:
		conn = psycopg2.connect(conn_string)		

	except (Exception, psycopg2.DatabaseError) as error:
			logger.debug(error)
	else:
		logger.debug("Successfully connected to db")
		# 1. Get url and timestamps 
		sql = """ 
			select url, article_read_date 
			from article
			where market_price is null;
		"""
		cur = conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		
		# DEBUG:db:rows is a <class 'list'>
		# DEBUG:db:a row is a <class 'tuple'>
		# DEBUG:db:url is a <class 'str'>
		# DEBUG:db:timestamp is a <class 'datetime.datetime'>

		# Now need to get price closest to time
		for row in rows:
			pass

		get_minute_close('DJI',row[1])


	finally:
		if conn is not None:
			conn.close()