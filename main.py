#!/usr/bin/env python3

import time
from scrapetweet import tweet_formatter, twitter_access, scrape
import requests
import traceback
import tweepy
import logging
import os
from pathlib import Path

cwd = Path(os.path.dirname(__file__))

try:
	os.mkdir(Path(cwd/'logs'))
except FileExistsError:
	pass

now_time = (time.strftime('%Y_%m_%d_%H:%M:%S'))

LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(
	filename=Path(cwd/'logs'/f'tfl_update_{now_time}.log'),
	level=logging.DEBUG,
	format=LOG_FORMAT
	)
logger = logging.getLogger()
logger.debug('Starting program')


def main():

	tf = tweet_formatter.TweetFormatter()

	while True:
		try:
			logger.debug('Scrape.')
			scrape_data = scrape.scrape_tfl_data()
		
		except requests.exceptions.ConnectTimeout as e:
			logger.debug('Connection timed out.')
			logger.debug(e)
			time.sleep(5)
			continue
		
		except AttributeError as e:
			logger.debug('HTML request timed out.')
			logger.debug(e)
			time.sleep(5)
			continue

		logger.debug('Pack tweets.')
		package = tf.format(scrape_data)
			
		if not package:
			logger.debug('''
				No update needed. All lines good 
				service or no change since previous scrape. 
				Check again in 5 min.
				''')
			time.sleep(300)
		
		else:
			try:
				logger.debug('Send tweet.')
				twitter_access.TwitterAccess().tweet(package)

			except tweepy.error.TweepError as e:
				logger.debug(traceback.format_exc())
				print('TweepError: ',e)
				pass

			logger.debug('Waiting 5 min until next scrape...')
			time.sleep(300)


if __name__ == '__main__':
	main()