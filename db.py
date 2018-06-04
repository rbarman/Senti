from config import postgres_config as p
from Market import get_minute_close
from Market import get_minute_close_batch
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
		
		close_prices = get_minute_close_batch('DJI',rows)
		# need to update the market price market_price column

		# for each row, update the market_price column 
			# rows and close_prices should always be same length
		for row, close in zip(rows, close_prices):
			try:
				sql = """ 
					UPDATE article
                	SET market_price = %s
                	WHERE url = %s
                """
				cur = conn.cursor()
				cur.execute(sql, (close,row[0],))
				conn.commit()
				cur.close()
			except (Exception, psycopg2.DatabaseError) as error:
				logger.debug(error)
			else:
				logger.info("Successfully updated market_price")

	finally:
		if conn is not None:
			conn.close()