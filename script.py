from News import News, Reuters
from Market import get_latest_close
import datetime
import pytz
import logging
import sched, time
s = sched.scheduler(time.time, time.sleep)

DELAY = 60 * 5

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

def main():

	logging.info("Current Time {:%H:%M}".format(now))
	logging.info("Market Hours: {:%H:%M}-{:%H:%M}".format(MARKET_START,MARKET_END))

	#s.enter(1, 1, scheduled_function, (s,))
	#s.run()

	# Test Case
	url = 'https://www.reuters.com/article/us-ukraine-russia-journalist/ukraine-and-russia-trade-accusations-over-killing-of-dissident-journalist-idUSKCN1IV1EO'
	article = Reuters.get_article(url)
	article.save()

# move to a log config file / dictionary?
def log_setup():
	log_file = 'logs/{}.log'.format(now)
	logging.basicConfig(filename=log_file, level=logging.INFO)
 
if __name__ == '__main__':
	log_setup()
	main()