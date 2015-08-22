import re
import os
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import defaultdict as dd

class RWScraper(object):
    def __init__(self):
        self.url = 'http://www.rotoworld.com/playernews/nfl/football-player-news'
        self._team_news = dd(lambda : dd(list))
        self.same_day = True
        self.date = (0, date.today().day, 0)

    def _get_player_info(self, player_box):
        date_str = player_box.select('.date')[0].contents[0]
        date = int(re.findall(r'^.* (\d+),.*$', date_str)[0])
        if date != self.date[1]:
            return False
        player_dict = {}
        player_info = player_box.select('.player a')
        player_dict['team'] = player_info[1].contents[0]
        player_dict['name'] = player_info[0].contents[0]
        player_dict['news'] = (player_box.select('p')[0].contents[0], 
                               player_box.select('.impact')[0].contents[0])
        return player_dict

    def _boxes_to_news(self, player_boxes):
        for player_box in player_boxes:
            player_dict = self._get_player_info(player_box)
            if not player_dict:
                return False
            self._team_news[player_dict['team']][player_dict['name']].append(player_dict['news'])
        return True

    def _get_player_news(self):
        driver = webdriver.PhantomJS()
        driver.get(self.url)
        if self.date[0]:
            date_picker = driver.find_element_by_id('tbDatepicker')
            date_picker.click()
            date_picker.send_keys('{}/{}/{}'.format(self.date[0], self.date[1], self.date[2]))
            driver.find_element_by_id('cp1_ctl01_btnFilterResults').click()
        while self.same_day:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            player_boxes = soup.select('.pb')
            self.same_day = self._boxes_to_news(player_boxes)
            driver.find_element_by_id('cp1_ctl01_btnNavigate1').click()

    def scrape(self, date='today'):
        if date != 'today':
            self.date = date
        self._get_player_news()
        os.remove('ghostdriver.log')

    def print_news(self, impact=False):
        for team in self._team_news.keys():
            print team
            for player in self._team_news[team].keys():
                for news in self._team_news[team][player]:
                    print '\t* ' + news[0]
                    if impact == True:
                        print '\t\t- ' + news[1].strip()
