import time
import scrapetweet as st
import requests
import traceback
import tweepy
import logging
import os
from pathlib import Path

# Make log dir, if it doesn't exist
cwd = Path(os.path.dirname(__file__))

try:
	os.mkdir(Path(cwd/'logs'))
except FileExistsError:
	pass

# Create and configure logger
now_time = (time.strftime('%Y_%m_%d_%H:%M:%S'))

LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(filename=Path(cwd/'logs'/f'tfl_update_{now_time}.log'),
					level=logging.DEBUG,
					format=LOG_FORMAT)
logger = logging.getLogger()
logger.debug('Starting program')

# -----------------------------------------------------------------

def main():
	tf = st.TweetFormatter()

	while True:

		try:
			logger.debug('Scrape.')
			scrape = st.scrape_tfl_data()
		
		except requests.exceptions.ConnectTimeout as e:
			logger.debug('Connection timed out.')
			time.sleep(5)
			continue
		
		except:
			logger.debug('Other scrape error.')
			time.sleep(5)
			continue

		try:
			logger.debug('Pack tweets.')
			package = tf.format(scrape)
			
			if not package:
				logger.debug('No issues to report. Check again in 5 min.')
				time.sleep(300)
				continue

		try:
			logger.debug('Tweet.')
			st.TwitterAccess().tweet(package)

		except tweepy.error.TweepError as e:
			logger.debug('TweepError - probably a duplicate tweet.')
			print(traceback.format_exc())
			pass

		logger.debug('Waiting 5 min until next scrape...')
		time.sleep(300)


if __name__ == '__main__':
	main()