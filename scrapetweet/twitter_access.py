import tweepy
from secure_keys import secure_keys, account


class TwitterAccess:
    '''Post tweets to Twitter.'''
    def __init__(self):
        self._keys = secure_keys
        self._account = account


    def _authenticate(self):
        '''Prepare Twitter authentication.

        Returns auth object which tweepy.API object
        accepts and uses to authenticate activity.
        '''
        auth = tweepy.OAuthHandler(self._keys['consumer_key'], self._keys['consumer_secret'])
        auth.set_access_token(self._keys['access_token'], self._keys['access_secret'])

        return auth


    def _api(self):
        '''Access Twitter API.'''
        api = tweepy.API(self._authenticate())
        return api


    def _get_latest_tweet_id(self):
        latest_tweet = self._api().user_timeline(id=self._account)
        return latest_tweet[0]._json['id']


    def tweet(self, messages):
        '''Tweet.

        If tweet exceeds char limit, surplus
        text is added as reply to thread.'''
        if type(messages) is str:
            self._api().update_status(messages)
        else:
            self._api().update_status(messages[0])
            tweet_id = self._get_latest_tweet_id()
            for msg in messages[1:]:
                self._api().update_status(self.account + msg, tweet_id)
