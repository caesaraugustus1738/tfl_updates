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
			print('Attempting to scrape...')
			logger.debug('Scrape.')
			
			scrape = st.scrape_tfl_data()
			
			print('Data scraped!\n')
		
		except requests.exceptions.ConnectTimeout as e:
			logger.debug('Connection timed out.')
			print('Connection has timed out - ',e)
			time.sleep(5)
			continue
		
		except:
			logger.debug('Other scrape error.')
			print('An error I cannot trace has occurred. Waiting 5 secs until next scrape attempt.')
			time.sleep(5)
			continue

		try:
			print('Attempting to package tweets...')
			logger.debug('Pack tweets.')
			
			package = tf.format(scrape)
			
			print('Tweets packaged!\n')
		except st.NoUpdateException as e:
			logger.debug('Nothing to update.')
			print('\n', e, '\n')
			pass

		try:
			print('Attempting to Tweet...')
			logger.debug('Tweet.')
			
			st.TwitterAccess().tweet(package)
			
			print('Tweet successful!\n')
		except tweepy.error.TweepError as e:
			logger.debug('TweepError - probably a duplicate tweet.')
			print(traceback.format_exc())
			pass

		print('Waiting 5 min until next scrape...')
		logger.debug('Waiting 5 min until next scrape...')
		time.sleep(300)

if __name__ == '__main__':
	main()