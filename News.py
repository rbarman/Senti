from bs4 import BeautifulSoup
import requests
from abc import ABCMeta, abstractmethod
import logging
import psycopg2
from config import postgres_config as p

# NLTK used in Article for prepocessing article text
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

################
# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
################

# NLTK
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()


# Abstract base class for news sources
#TODO: differentiate between NewsFeed and NewsArticle?
class News(metaclass=ABCMeta):

	@staticmethod 
	# should be class method?
	def read_and_save_feed():
		logger.info("Reading Feed...")
		sources = [Reuters]
		for source in sources: 
			for article_url in source.get_article_urls():
				article = source.get_article(article_url)
				# TODO: have a batch save? Currently opens and closes db connection for each article 
				article.save()

	@abstractmethod
	def soupify(url):
		source = requests.get(url).text
		soup = BeautifulSoup(source,"lxml")
		return soup

	@abstractmethod
	def get_article_urls():
		pass

	# naively getting article text from the p tags
	@abstractmethod
	def get_article(article_url):
		soup = News.soupify(article_url)
		article_text = ""
		for p in soup.find_all('p'):
			article_text = article_text + p.text + " "

		article_title = soup.find('title').text + ".txt"
	
		# TODO: https://stackoverflow.com/questions/1336791/dictionary-vs-object-which-is-more-efficient-and-why#1336890
		article = Article(article_url,article_title,article_text)
		return article

class Reuters(News):

	def __init__(self):
		pass

	@staticmethod
	def get_article_urls():
		# the wire gives the latest news
		url = 'https://www.reuters.com/theWire'
		soup = News.soupify(url)

		urls = [] 
		for link in soup.find_all('a'):
			link_url = link.get('href')
			# sample link we want: https://www.reuters.com/article/us-northkorea-missiles/south-korea-says-north-korea-committed-to-complete-denuclearisation-summit-with-trump-idUSKCN1IS01K
			if(link_url.startswith('https://www.reuters.com/article/')):
				urls.append(link_url)
		urls = set(urls) # only want uniques
		logger.info("Got {} articles from {}".format(len(urls),url))
		return urls

class Article(object):
	def __init__(self, url, title,text):
		self.url = url
		self.title = title
		self.text = self.filter_and_stem_text(text)
		logger.info("Created Article : {}".format(self.url))		

	# Preprocess the article text for future ml 
	def filter_and_stem_text(self, text):
		logger.debug("Removing Stop Words")
		filtered_sentences = []
		for sentence in sent_tokenize(text):
			filtered_sentence = []
			for word in word_tokenize(sentence):
				if word not in stop_words:
					filtered_sentence.append(word)
			filtered_sentences.append(filtered_sentence)

		for sentence in filtered_sentences:
			logger.debug("{}\n".format(sentence))

		####
		# Stemming words in each sentence
		###
		logger.debug("Stemming sentences")
		stemmed_sentences = []
		for sentence in filtered_sentences:
			stemmed_sentence = []
			for word in sentence:
				stemmed_sentence.append(ps.stem(word))
			stemmed_sentences.append(stemmed_sentence)

		for sentence in stemmed_sentences:
			logger.debug(sentence)

		# Stemmed_sentences is a list of list of strs
		# Convert stemmed_sentences into one string
		sentence_strings = []
		for sentence in stemmed_sentences:
			sentence_strings.append(' '.join(sentence))

		full_sentence_string = ' '.join(sentence_strings)
		logger.debug(full_sentence_string)

		return full_sentence_string

	# saves Article to db
	def save(self):
		logger.debug("in save()")
		conn_string = "host='{}' dbname='{}' user='{}' password='{}'".format(p.get('host'),p.get('dbname'),p.get('user'),p.get('password'))
		logger.debug(conn_string)
		conn = None
		try:
			conn = psycopg2.connect(conn_string)		

			# upserting to avoid adding duplicate articles
			sql = "INSERT INTO article(url,text) VALUES(%s,%s) ON CONFLICT DO NOTHING"

			cur = conn.cursor()
			cur.execute(sql, (self.url,self.text,))

			conn.commit()
			cur.close()
		except (Exception, psycopg2.DatabaseError) as error:
			logger.debug(error)
		else:
			logger.info("Successfully entered into db")
		finally:
			if conn is not None:
				conn.close()

	def save_to_file(self,directory):
		try:
			with open("{}{}".format(directory,article.title), "w") as text_file:
				print(article.text, file=text_file)
				logger.info("Saved Article {}{}".format(directory,article.title))
		except FileNotFoundError as e:
			print("FileNotFoundError w/ {}".format(article.url))		
