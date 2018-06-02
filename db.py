from config import postgres_config as p
import logging
import psycopg2
################
# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
################

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
