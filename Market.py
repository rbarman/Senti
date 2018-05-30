from config import alphavantage
# https://github.com/RomelTorres/alpha_vantage
	# # https://stackoverflow.com/questions/10040954/alternative-to-google-finance-api
from alpha_vantage.timeseries import TimeSeries
import logging

################
# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
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
