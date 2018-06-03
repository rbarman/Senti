from config import alphavantage
# https://github.com/RomelTorres/alpha_vantage
	# # https://stackoverflow.com/questions/10040954/alternative-to-google-finance-api
from alpha_vantage.timeseries import TimeSeries
import logging

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

def get_minute_close(symbol,time):
	logger.debug(time)
	ts = TimeSeries(key=alphavantage.get('API_KEY'),output_format='pandas')
	data, meta_data = ts.get_intraday(symbol=symbol,interval='1min')
	latest = data.head(1)
	logger.debug(latest)
	#logger.debug("an article time:  {} is a : {}".format(time,type(time)))
	logger.debug(data.index.values)
	logger.debug(type(data.index.values))
	logger.debug(type(data.index.values[1]))
	#DEBUG:Market:<class 'numpy.ndarray'>
	#DEBUG:Market:<class 'str'>
	# the time index returned is a str...
	# will need to change time format to match for str comparison...
	# or use datetime for direct comparison?



