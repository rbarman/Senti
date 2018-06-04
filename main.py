from News import News
from db import set_market_price
import datetime
import pytz
import logging
import sched, time
import sys, getopt
from test import test_main
s = sched.scheduler(time.time, time.sleep)

# Better place to put globals?
DELAY = 10 * 5
eastern = pytz.timezone('US/Eastern')
now = datetime.datetime.now(eastern)
# Market Hours are 9:30 a.m. to 4:00 p.m. (Eastern Time)
MARKET_START = now.replace(hour=9,minute=30,second=0,microsecond=0)
MARKET_END = now.replace(hour=16,minute=00,second=0,microsecond=0)

def scheduled_function(sc):
	# Currently loops through out day and accesses feed during market hours
	# OR... start script on trading hours and just check for MARKET_END
	if (now > MARKET_START) & (now < MARKET_END):
		News.read_and_save_feed()
	else:
		logging.info("Market is currently closed")
	s.enter(DELAY, 1, scheduled_function, (sc,))

def main(argv):

	logging.info("Current Time {:%H:%M}".format(now))
	logging.info("Market Hours: {:%H:%M}-{:%H:%M}".format(MARKET_START,MARKET_END))

	# command line arguments 
		# -t for test, -p or none for production
	try:
		opts, args = getopt.getopt(argv,"ptm")
	except getopt.GetoptError:
		logging.exception("error getting options")
		sys.exit(2)

	for opt, arg in opts:

		if opt == '-t':
			logging.info("Test")
			test_main() # main wrapper func for tests
			sys.exit(2)

		elif opt == '-m':
			logging.info("Setting Market prices")
			set_market_price()
			sys.exit(2)

		else: # could also use -p tag
			logging.info('Production')
			s.enter(1, 1, scheduled_function, (s,))
			s.run()
			sys.exit(2)

# move to a log config file / dictionary?
def log_setup():
	# TODO: add a stream handler?
	log_file = 'logs/{}.log'.format(now)
	logging.basicConfig(filename=log_file, level=logging.INFO)
 
if __name__ == '__main__':
	log_setup()
	main(sys.argv[1:]) # accept command line arguments