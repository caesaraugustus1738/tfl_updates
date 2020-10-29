import json
from string import ascii_letters as ascii_letters
from utils import utils

class TweetFormatter:
    '''Format scraped data into tweets.

    Accepts a dict of dicts supplied by
    Scraper class.
    '''
    def __init__(self):
        self._header = '🚇 Tube updates 🚇'
        self._footer = 'https://tfl.gov.uk/tube-dlr-overground/status/#'
        self._char_limit = 270 - len(self._header + self._footer) - 3
        self._line_cutoff = 50
        self._good_service = 'Good service'
        self._warning_emj = '⚠'
        self._tick_emj = '✅'
        self._short_sum = 'short_sum'
        self.prev_scrape = {}


    def format(self, scrape_data):
        '''Format scraped data to be tweet ready.

        Convert scraped data into lst of 
        ready-to-tweet strs.
        '''
        alerts = self.categorise_alerts(scrape_data, self.prev_scrape)
        self.prev_scrape = scrape_data
        if utils.truly_empty(alerts):
            print('''No updates. Either all lines good service, or no change since previous scrape.''')
            return None

        alerts_formatted = self._format_alerts(alerts)
        tweet_groups = self._tweet_grouper(alerts_formatted)
        
        return self._tweet_parcel(tweet_groups)


    def categorise_alerts(self, upd, prev_upd=None):
        '''Returns a dict dicts with categorise alerts.

        Accepts up to two dicts. Compares
        and groups updates. Passing one dict
        checks for anything which is not a 
        good service.
        '''
        alerts =    {
                        'fixed': {}, 
                        'new': {},
                    }

        if not prev_upd:
            print('First scrape of the session!')
            for key in upd:
                if upd[key] != self._good_service:
                    alerts['new'][key] = upd[key]
        else:
            for key in upd:
                if upd[key] == prev_upd[key]:
                    pass
                elif upd[key] == 'Good service':
                    alerts['fixed'][key] = upd[key]
                else:
                    alerts['new'][key] = upd[key]

        return alerts


    def _format_alerts(self, alerts):
        '''Converts a dict of dicts to a list of formatted strs.

        Wants a dict 'alerts' object created by categorise_alerts().
        Prefixes tube updates with appropriate emoji.
        '''
        emoji_adder = lambda lst, dict_, emj: lst.append(self._nice_msg(dict_, emoji=emj))

        alert_cats = []
        for category in alerts:
            if category == 'fixed':
                emoji_adder(alert_cats, alerts[category], self._tick_emj)
            elif category == 'new':
                emoji_adder(alert_cats, alerts[category], self._warning_emj)

        flatten_list = lambda lst: [item for sublist in lst for item in sublist]

        alert_list = flatten_list(alert_cats)

        return alert_list


    def _nice_msg(self, dict_, emoji=None):
        '''Convert dict key/value pairs to strs.'''
        nice_msg = []

        for key in dict_:
            nice_msg.append(key + ' - ' + dict_[key])
            if emoji:
                nice_msg[-1] = emoji + ' ' + nice_msg[-1]

        return nice_msg


    def _tweet_grouper(self, alerts):
        '''Groups strs into lists based on Twitter char limit.

        Accepts a list of strs.
        '''
        counter = 0
        tweet_groups = [[]]

        for alert in alerts:
            if len(alert) > self._char_limit:
                raise Exception(f'Item: {alert} has illegal length.')
            
            counter += len(alert)
            if counter <= self._char_limit:
                tweet_groups[-1].append(alert)
            else:
                tweet_groups.append([alert])
                counter = len(alert)
        
        return tweet_groups


    def _tweet_parcel(self, _list):
        '''Convert tweet_groups lists to tweet-ready strs.

        For each tweet: add line breaks, add header/footer,
        add counter, convert list of lines to single str.
        '''
        tweet_parcel = []

        for num, val in enumerate(_list):
            part_of = f' {num+1}/{len(_list)}'
            _list[num].insert(0, self._header + part_of)
            _list[num].append(self._footer)

        for i in _list:
            tweet_parcel.append('\n'.join(i))

        return tweet_parcel