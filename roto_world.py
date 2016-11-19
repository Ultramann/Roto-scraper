import re
import os
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from colored import fg, bg, attr
from collections import defaultdict as dd

class RWScraper(object):
    '''
    Class for grabbing player news from www.rotoworld.com/playernews/nfl/football-player-news
    for any given day, default is the current day. 
    Methods: scrape -     If a specific day is to be specified for scraping, 
                          it should be formatted as a tuple: 
                            (month, day, year)
                          and passed to the scrape method through the date argument.

             print_news - Used once scrape has been called, the corresponding day's data is stored
                          on the instance. By default, does not print the impact section of the
                          player news segments. To print the impact section, pass True to the
                          impact argument.

    Dependencies:         selenium
                          colored
                          bs4
    '''
    def __init__(self):
        self.url = 'http://www.rotoworld.com/playernews/nfl/football-player-news'
        self._team_news = dd(lambda : dd(list))
        self._same_day = True
        self._date = (0, date.today().day, 0)

    def _get_player_info(self, player_box):
        date_str = player_box.select('.date')[0].contents[0]
        date = int(re.findall(r'^.* (\d+)[ ,].*$', date_str)[0])
        if date != self._date[1]:
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
        if self._date[0]:
            date_picker = driver.find_element_by_id('tbDatepicker')
            date_picker.click()
            date_picker.send_keys('{}/{}/{}'.format(self._date[0], self._date[1], self._date[2]))
            driver.find_element_by_id('cp1_ctl00_btnFilterResults').click()
        while self._same_day:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            player_boxes = soup.select('.pb')
            self._same_day = self._boxes_to_news(player_boxes)
            driver.find_element_by_id('cp1_ctl00_btnNavigate1').click()
        driver.quit()

    def scrape(self, date='today'):
        if date != 'today':
            self._date = date
        self._get_player_news()
        os.remove('ghostdriver.log')

    def print_news(self, impact=False):
        tcd = {'Broncos':   {'fg': 208, 'bg': 18},
               'Vikings':   {'fg': 11, 'bg': 54},
               'Falcons':   {'fg': 0, 'bg': 1},
               'Saints':    {'fg': 0, 'bg': 136},
               'Chargers':  {'fg': 226, 'bg': 21},
               'Lions':     {'fg': 27, 'bg': 244}, 
               'Cowboys':   {'fg': 244, 'bg': 27}, 
               'Browns':    {'fg': 202, 'bg': 52},
               'Eagles':    {'fg': 231, 'bg': 29},
               'Steelers':  {'fg': 0, 'bg': 11}, 
               'Giants':    {'fg': 9, 'bg': 19},
               'Patriots':  {'fg': 9, 'bg': 19},
               'Buccaneers':{'fg': 0, 'bg': 9}, 
               'Cardinals': {'fg': 0, 'bg': 1},
               'Chiefs':    {'fg': 0, 'bg': 196},
               'Jaguars':   {'fg': 11, 'bg': 30},
               'Redskins':  {'fg': 231, 'bg': 88},
               'Jets':      {'fg': 231, 'bg': 22},
               'Ravens':    {'fg': 11, 'bg': 55},
               'Colts':     {'fg': 15, 'bg': 18},
               'Packers':   {'fg': 11, 'bg': 22},
               'Titans':    {'fg': 231, 'bg': 4},
               'Free Agent':{'fg': 0, 'bg': 231},
               'Bills':     {'fg': 231, 'bg': 27},
               'Texans':    {'fg': 18, 'bg': 196},
               '49ers':     {'fg': 15, 'bg': 124},
               'Seahawks':  {'fg': 10, 'bg': 21},
               'Panthers':  {'fg': 0, 'bg': 33},
               'Dolphins':  {'fg': 208, 'bg': 29},
               'Bengals':   {'fg': 0, 'bg': 202},
               'Rams':      {'fg': 184, 'bg': 19},
               'Raiders':   {'fg': 0, 'bg': 247},
               'Bears':     {'fg': 208, 'bg': 17},
               'Player':    {'fg': 0, 'bg': 180}}
        for team in self._team_news.keys():
            print('%s%s %s %s' % (fg(tcd[team]['fg']), bg(tcd[team]['bg']), team, attr(0)))
            for player in self._team_news[team].keys():
                for news in self._team_news[team][player]:
                    print('\t* ' + news[0])
                    if impact == True:
                        print('\t\t- ' + news[1].strip())
