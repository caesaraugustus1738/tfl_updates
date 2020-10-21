import time
import scrapetweet_v2 as st
import requests
import traceback
import tweepy

def main():
	tweet_format = st.FormatTweet()

	while True:
		print(tweet_format.previous_scrape)

		try:
			print('Attempting to scrape...')
			scrape = st.scrape()
			print('Data scraped!\n')
		except requests.exceptions.ConnectTimeout as e:
			print('Connection has timed out - ',e)
			time.sleep(5)
			continue
		except:
			print('An error I cannot trace has occurred. Waiting 5 secs until next scrape attempt.')
			time.sleep(5)
			continue

		try:
			print('Attempting to package tweets...')
			package = tweet_format.package_tweets(scrape)
			print('Tweets packaged!\n')
		except st.NoUpdateException as e:
			print('\n', e, '\n')
			pass

		try:
			print('Attempting to Tweet...')
			st.Tweeter().tweet(package)
			print('Tweet successful!\n')
		except tweepy.error.TweepError as e:
			print(traceback.format_exc())
			pass

		print('Waiting 5 min until next scrape...')
		time.sleep(300)

if __name__ == '__main__':
	main()