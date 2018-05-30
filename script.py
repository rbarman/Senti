from News import News
import datetime
import logging
import sched, time
s = sched.scheduler(time.time, time.sleep)

DELAY = 60 * 5

def scheduled_function(sc):
	News.read_and_save_feed()
	s.enter(DELAY, 1, looper, (sc,))

def main():
	#########################
	# Log Setup
	# TODO: move log setup to a log config
	log_file = 'logs/{}.log'.format(datetime.datetime.now())
	logging.basicConfig(filename=log_file, level=logging.INFO)
	#########################

	s.enter(1, 1, scheduled_function, (s,))
	s.run()

if __name__ == '__main__':
    main()