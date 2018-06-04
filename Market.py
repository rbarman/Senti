from config import alphavantage
# https://github.com/RomelTorres/alpha_vantage
	# # https://stackoverflow.com/questions/10040954/alternative-to-google-finance-api
from alpha_vantage.timeseries import TimeSeries
import logging
from datetime import timedelta

################
# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
################

# DJI, SPX
def get_latest_close(symbol):
	ts = TimeSeries(key=alphavantage.get('API_KEY'),output_format='pandas')
	data, meta_data = ts.get_intraday(symbol=symbol,interval='1min')
	latest = data.head(1) # get the latest minute
	close = latest['4. close'] # get the close column
	close = close.values[0] # get the actual value
	logger.info("current price is {}".format(close))
	return close

# Get minute close for rows
	# rows have url and time(DateTime)
	# used by db.set_market_price()
def get_minute_close_batch(symbol,rows):
	logger.debug("get_minute_close_batch")

	ts = TimeSeries(key=alphavantage.get('API_KEY'),output_format='pandas')
	data, meta_data = ts.get_intraday(symbol=symbol,interval='1min', outputsize='full')

	close_prices = []
	future_close_5mins = []
	future_close_30mins = []
	future_close_1hrs = []

	for row in rows:
		time = row[1]
		close = get_minute_close_(symbol,time,data)
		# TEST
		# https://stackoverflow.com/questions/6205442/how-to-find-datetime-10-mins-after-current-time#6205529
		future_close_5min = get_minute_close_(symbol,time + timedelta(minutes = 5),data)
		future_close_30min = get_minute_close_(symbol,time + timedelta(minutes = 30),data)
		future_close_1hr = get_minute_close_(symbol,time + timedelta(hours = 1),data)

		# add
		close_prices.append(close)
		future_close_5mins.append(future_close_5min)
		future_close_30mins.append(future_close_30min)
		future_close_1hrs.append(future_close_1hr)

	logger.debug("Returning close_prices")
	# return dictionary w/ each prices
	prices = {
		'close_prices': close_prices, 
		'future_close_5mins': future_close_5mins,
		'future_close_30mins': future_close_30mins,
		'future_close_1hrs': future_close_1hrs
	}
	return prices

def get_minute_close_(symbol,time,df):
	# search for the time in df to get close
	new_dt = time.replace(second = 0)
	new_str_time = new_dt.strftime('%Y-%m-%d %H:%M:%S')

	obs = None
	try:
		obs = df.loc[new_str_time]
	# KeyError when df does not contain this date
	except (Exception, KeyError) as error:
		logger.debug(error)
		# TODO: Better value to add? 
			# Eventually would have to remove this row from db table if the article time is outside of market hours?
		return -1
	else:
		close = obs['4. close']
		#logging.info("The close at {} is {}".format(new_str_time,close))
		return close;


#TODO: accept an array of times to avoid
	# ValueError: Please consider optimizing your API call frequency.
def get_minute_close(symbol,time):
	logger.debug(time)
	ts = TimeSeries(key=alphavantage.get('API_KEY'),output_format='pandas')
	data, meta_data = ts.get_intraday(symbol=symbol,interval='1min', outputsize='full')

	# the returned data will be a dataframe 
		# index is a time string with format: '2018-06-01 14:22:00'
		# columns are open, close, etc

	# convert the datetime object to a string that matches the index format
		# example: 
	new_dt = time.replace(second = 0)
	new_str_time = new_dt.strftime('%Y-%m-%d %H:%M:%S')

	# use this string to search the data by index
	obs = None
	try:
		obs = data.loc[new_str_time]
	# KeyError when data does not contain this date
	except (Exception, KeyError) as error:
		logger.debug(error)
		return None 
	else:
		close = obs['4. close']
		logging.info("The close at {} is {}".format(new_str_time,close))
		return close
