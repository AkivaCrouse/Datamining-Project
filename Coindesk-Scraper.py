######################################################################################################################
"""
Title: Coindesk.com Scraper
Authors: Akiva Crouse & Ohad Ben Tzvi
Date: 23/06/2021
"""
######################################################################################################################


import requests
import time
import textwrap as tw
import argparse
import sys
from tabulate import tabulate
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime


# PATH = "C:\Program Files (x86)\chromedriver.exe"
ARTICLE_LINK_INDEX = 1
URL = "https://www.coindesk.com"
TAGS = 0
DATETIME = 1
REQUIRED_NUM_OF_ARGS = 3
ARG_OPTION = 1
MAX_ARTICLES = 1000
ARTICLES_PER_HOME = 9
ARTICLES_PER_PAGE = 12
DEFAULT_PREFIX = '/category/'
SLEEPTIME = 3


def welcome():
    """
    Gets the section and number of articles required by the user, with argparser,
    and outputs the relevant URL suffix for these articles together with the number of articles.
    the program also response to the flag -h for help.
    :return:    section: relevant section URL suffix.
                num_articles: number of articles requested by the user
    """

    # Overriding error function in order to display the help message
    # whenever the error method is triggered, for UX purposes.
    class MyParser(argparse.ArgumentParser):
        """
        Overriding the 'error' function in ArgumentParser in order to display the help message
        whenever the error method is triggered, for UX purposes.
        """

        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    section_dict = {
        'tech': DEFAULT_PREFIX + 'tech',
        'business': DEFAULT_PREFIX + 'business',
        'people': DEFAULT_PREFIX + 'people',
        'regulation': DEFAULT_PREFIX + 'policy-regulation',
        'features': '/features',
        'markets': '/markets',
        'opinion': '/opinion',
        'latest': '/news',
    }
    coindesk_reader = MyParser(add_help=False)
    coindesk_reader.add_argument('section', type=str.lower, metavar='section',
                                 help='Choose one of the following sections: latest, tech, business, regulation, people, '
                                      'features, opinion, markets.',
                                 choices=['latest', 'tech', 'business', 'regulation', 'people', 'opinion', 'markets'])
    coindesk_reader.add_argument('num_articles', type=float, metavar='num_articles', help=f'Number of articles, from 1 to {MAX_ARTICLES}',
                                 choices=list(range(1, MAX_ARTICLES+1)))
    args = coindesk_reader.parse_args()
    section = args.section
    num_articles = int(args.num_articles)

    return section_dict[section], num_articles


def get_html(url, num_articles):
    """Receives the url to coindesk.com.
    Opens the url using Chrome driver.
    Clicks on the 'MORE' button several times.
    Returns the page source code as html,"""
    # browser = webdriver.Chrome(PATH)
    browser = webdriver.Chrome()
    browser.get(url)
    scrolls = (num_articles - ARTICLES_PER_HOME)//ARTICLES_PER_PAGE + 1
    for click_more in range(scrolls):
        try:
            more_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cta-story-stack")))

        except Exception:
            print("Articles did not load in time due to network.")
            browser.close()
            sys.exit(1)

        more_button.click()
        time.sleep(SLEEPTIME)


    html = browser.page_source
    return html


def get_link(article_html):
    """Gets the block of html for each article and returns the url to the article"""
    links = [link.get('href') for link in article_html.find_all('a')]
    return URL + links[ARTICLE_LINK_INDEX]


def get_tags(article_link):
    """
    Receives a url to an article.
    Retrieves the url source code as html.
    Scrapes and returns the articles topic tags.
    :param article_link: str
    :return: list of strings
    """
    sub_r = requests.get(article_link)
    sub_soup = BeautifulSoup(sub_r.content, 'html.parser')
    tags_tag = sub_soup.find('div', class_='tags')
    tags = [tag.get_text() for tag in tags_tag.find_all('a')]
    return tags


def article_scrape(article_link):
    """
    Receives a url to an article.
    Retrieves the url source code as html.
    Scrapes and returns the articles topic tags.
    :param article_link: str
    :return: list of strings
    """
    sub_r = requests.get(article_link)
    sub_soup = BeautifulSoup(sub_r.content, 'html.parser')
    tags_tag = sub_soup.find('div', class_='tags')
    tags = [tag.get_text() for tag in tags_tag.find_all('a')]
    datetime = sub_soup.find('time').get('datetime')
    return tags, datetime


def scrape(html, num_articles):
    """
    Receives html script and number of articles to print.
    Parses the html and prints the following subjects per article for the number of articles requested:
        Title, Summary, Author, Link, Tags and Date-Time
    :param html: html string
    :param num_articles: int
    """
    soup = BeautifulSoup(html, 'html.parser')
    count = 0
    for article in soup.find_all('div', class_='text-content'):
        count += 1
        article_number = ['#', count]
        table = [
            ['Title', article.h4.text],
            ['Summary', '\n'.join(tw.wrap(article.p.text, width=90))],
            ['Author', ', '.join([author.get_text() for author in article.find_all('span', class_='credit')])],
            ['Link', get_link(article)],
            ['Tags', ', '.join(article_scrape(get_link(article))[TAGS])],
            ['Date-Time', article_scrape(get_link(article))[DATETIME]]
        ]
        print('\n', tabulate(table, article_number, tablefmt='plain'))
        if count == num_articles:
            break


def main():
    """Receives Coindesk topic section and number of articles to print as command parameters.
    Uses selenium to retrieve the required html script.
    Scrapes and prints each article for the following data:
        Title, Summary, Author, Link, Tags and Date-Time"""
    section, num_arts = welcome()
    html = get_html(URL+section, num_arts)
    scrape(html, num_arts)


if __name__ == '__main__':
    main()