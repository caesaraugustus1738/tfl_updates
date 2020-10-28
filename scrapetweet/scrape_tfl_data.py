import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from html import unescape


def scrape_tfl_data(url='https://tfl.gov.uk/tube-dlr-overground/status/#'):
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