from config import postgres_config as p
import logging
import psycopg2
################
# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
################
from Market import get_latest_close


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

		# get current market price
		market_price = get_latest_close('SPX')

		# save all articles w/ current market price
		print(type(articles))
		for article in articles:
			print(type(article))
			# try:
			# 	conn = psycopg2.connect(conn_string)		

			# 	# upserting to avoid adding duplicate articles
			# 	sql = "INSERT INTO article(url,text,market_price) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING"

			# 	cur = conn.cursor()
			# 	cur.execute(sql, (article.url,article.text,market_price,))

			# 	conn.commit()
			# 	cur.close()
			# except (Exception, psycopg2.DatabaseError) as error:
			# 	logger.debug(error)
			# else:
			# 	logger.info("Successfully entered into db")

	finally:
		if conn is not None:
			conn.close()
