from config import alphavantage
# https://github.com/RomelTorres/alpha_vantage
	# # https://stackoverflow.com/questions/10040954/alternative-to-google-finance-api
from alpha_vantage.timeseries import TimeSeries

# DJI, SPX
def get_latest_close(symbol):
	ts = TimeSeries(key=alphavantage.get('API_KEY'),output_format='pandas')
	data, meta_data = ts.get_intraday(symbol=symbol,interval='1min')
	latest = data.head(1) # get the latest minute
	close = latest['4. close'] # get the close column
	close = close.values[0] # get the actual value
	return close
