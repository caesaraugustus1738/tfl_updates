import requests
import tweepy
import json
from pprint import pprint as pp
from secure_keys import secure_keys
from string import ascii_letters as ascii_letters
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from pprint import pprint as pp
from html import unescape


class NoUpdateException(Exception):
    pass


def scrape_travel_data(url='https://tfl.gov.uk/tube-dlr-overground/status/#'):
    '''Scrape travel updates from TFL website.'''
    _short_sum = 'short_sum'
    _good_service = 'Good service'


    def _tfl_soup(url):
        '''Return a parsed HTML object.'''
        try:
            html_res = requests.get(url, timeout=5)
        except requests.exceptions.ReadTimeout as e:
            print(e)
            return

        soup = bs(html_res.text, 'html.parser')

        return soup  
        

    def _tube_status(url):
        '''TFL updates from soup object.'''
        tube_line_status = {}
        soup = _tfl_soup(url)

        # Get tube line names
        link_tags = soup.find_all('li')

        for link in link_tags:
            if link.has_attr('aria-level'):
                line = link.find(class_='service-name').text.strip()
                summary = link.find(class_='disruption-summary').text.strip()
                tube_line_status[line] = summary

        return tube_line_status

    return _tube_status(url)


class TwitterAccess:
    '''Post tweets to Twitter.'''
    def __init__(self):
        self._keys = secure_keys


    def authenticate(self):
        '''Prepare Twitter authentication.

        Returns auth object which tweepy.API object
        accepts and uses to authenticate activity.'''
        auth = tweepy.OAuthHandler(self._keys['consumer_key'], self._keys['consumer_secret'])
        auth.set_access_token(self._keys['access_token'], self._keys['access_secret'])

        return auth


    def api(self):
        '''Access Twitter API.'''
        api = tweepy.API(self.authenticate())
        return api


    def tweet(self, messages):
        '''Tweet.'''
        if type(messages) is str:
            self.api().update_status(message)
        else:
            for m in message:
                self.api().update_status(m)


# Rename to TweetFormatter
class FormatTweet:
    '''Format scraped data into tweets.

    Accepts a dict of dicts supplied by
    Scraper class.'''
    def __init__(self):
        self._header = '🚇 Tube updates 🚇'
        self._footer = 'https://tfl.gov.uk/tube-dlr-overground/status/#'
        self._char_limit = 270 - len(self._header + self._footer) - 3
        self._line_cutoff = 50
        self._good_service = 'Returned to good service.'
        self._warning_emj = '⚠'
        self._tick_emj = '✅'
        self._short_sum = 'short_sum'
        self.previous_scrape = {}


    def categories(self, scrape_data):
        '''List of individual updates.

        Accepts dict of dicts. Compares 
        previous dict to new dict to help 
        craft new updates.'''

        if scrape_data == self.previous_scrape:
            raise NoUpdateException('No new TfL updates.')
        
        scrape_data_cats = []

        # Remove any good services from prev update
        self._rm_good_service()

        # Determine update category
        # Rename cats to alert > normal, alert > alert, normal > alert 
        categories = {
                'normal': self._return_to_normal(self.previous_scrape, scrape_data),
                'changes': self._update_change(self.previous_scrape, scrape_data),
                'alerts': self._new_updates(self.previous_scrape, scrape_data)
                }

        # Format updates based on category
        for cat in ['changes', 'alerts']:
            for msg in categories[cat]:
                scrape_data_cats.append(self.msg_formatter(msg, emoji=self._warning_emj))

        for msg in categories['normal']:
            scrape_data_cats.append(self.msg_formatter(msg, emoji=self._tick_emj)) 

        return scrape_data_cats


    def replace_scrape(self, scrape_data):
        self.previous_scrape = scrape_data


    def _rm_good_service(self):
        '''Remove good service from previous tweet.

        Need to use a .copy() because
        dict is being shrunk as we iterate.'''
        for key in self.previous_scrape.copy():
            if self.previous_scrape[key][self._short_sum] == self._good_service:
                del self.previous_scrape[key]


    def _return_to_normal(self, prev_upd, new_upd):
        '''Line returned to good service.'''
        for key in prev_upd:
            if key not in new_upd:
                yield self.msg_formatter(key, self._good_service)


    def _update_change(self, prev_upd, new_upd):
        '''Line with existing issue has new issue.'''
        for key in new_upd:
                if key in prev_upd:
                    if new_upd[key][self._short_sum] == prev_upd[key][self._short_sum]:
                        pass
                    else:
                        yield self.msg_formatter(key, new_upd[key][self._short_sum])


    def _new_updates(self, prev_upd, new_upd):
        '''Good line has new issue.'''
        for key in new_upd:
            if key not in prev_upd:
                yield self.msg_formatter(key, new_upd[key][self._short_sum])


    def msg_trimmer(self, msg_list):
        '''Trims string to cutoff.

        Accepts a list of strs. Finds
        appropriate place to trim str
        and adds '...' suffix.'''

        msg_list_cut = msg_list
        for num, val in enumerate(msg_list):
            if len(val) > self._line_cutoff:
                f_index = val.find(' ', self._line_cutoff)
                b_index = val.rfind(' ', 0, self._line_cutoff)
                abs_diff_func = lambda list_val: abs(list_val - self._line_cutoff)
                closest_val = min([f_index, b_index], key=abs_diff_func)
                trimmed_msg = val[:closest_val].strip()
                
                if trimmed_msg[-1] not in ascii_letters:
                    trimmed_msg = trimmed_msg[:-1]
                msg_list_cut[num] = trimmed_msg + '...'

        return msg_list_cut


    def msg_formatter(self, *args, emoji=None):
        '''Joins strs together with - dividers.

        Optional emoji prefix.'''
        msg = []
        for i in args:
            msg.append(i)
        if emoji:
            return emoji + ' ' + ' - '.join(msg)
        else:
            return ' - '.join(msg)


    def msg_grouper(self, msgs):
        '''Groups updates based on Twitter char limit.

        Accepts a list of strs.'''
        counter = 0
        split_list = [[]]
        for item in msgs:
            if len(item) > self._char_limit:
                raise Exception(f'Item: {item} has illegal length.')
            counter += len(item)
            if counter <= self._char_limit:
                split_list[-1].append(item)
            else:
                split_list.append([item])
                counter = len(item)
        return split_list


    def package_tweets(self, scrape_data):
        '''
        Put all data together in a list of lists.

        Ready to be uploaded.
        '''
        msgs_list = self.categories(scrape_data)
        self.replace_scrape(scrape_data)
        msgs_list_trim = self.msg_trimmer(msgs_list)
        msgs_grouped = self.msg_grouper(msgs_list_trim)

        for num, val in enumerate(msgs_grouped):
            part_of = f' {num+1}/{len(msgs_grouped)}'
            msgs_grouped[num].insert(0, self._header + part_of)
            msgs_grouped[num].append(self._footer)

        tweet_packet = []

        for i in msgs_grouped:
            tweet_packet.append('\n'.join(i))

        return tweet_packet
