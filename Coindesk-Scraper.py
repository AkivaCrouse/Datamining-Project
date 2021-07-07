######################################################################################################################
"""
Title: Coindesk.com Scraper
Authors: Akiva Crouse & Ohad Ben Tzvi
Date: 23/06/2021
"""
######################################################################################################################

import pymysql
import argparse
import sys
import textwrap as tw
import time
import datetime
from config import *
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate
import tqdm


class Article:
    """
        A class to represent an article.

        Attributes
        ----------
        article_id : int
            Number article instance created.
        name: str
            Article title.
        summary: str
            Article summary.
        author: str or list of strings
            Article author(s).
        link: str
            Link to article webpage (url).
        tags: list of str
            Article hashtags.
        date_published: datetime
            Date and time article was published.
        Methods
        -------
        set_tags_and_date(article_link):
            Receives the article url and sets the tags and date published
        get_link():
            Returns article link (str)
        get_article_id(self):
            Returns article id (int)
        """
    article_id = 0

    def __init__(self, article_html):
        """
        Constructs all necessary attributes of the vehicle object.
        :param article_html: article related html parsed from the main html.
        """
        Article.article_id += 1
        self.article_html = article_html
        self.article_id = Article.article_id
        self.name = article_html.h4.text
        self.summary = article_html.p.text
        self.author = [author.get_text() for author in article_html.find_all('span', class_='credit')]
        links = [link.get('href') for link in article_html.find_all('a')]
        self.link = URL + links[ARTICLE_LINK_INDEX]
        self.tags = None
        self.date_published = None
        self.set_tags_and_date()

    def __str__(self):
        """
        Constructs a table when print is called on the article.
        :return: table
        """
        return tabulate(tabular_data=[
            ['Title', self.name],
            ['Summary', '\n'.join(tw.wrap(self.summary, width=90))],
            ['Author', ', '.join(self.author)],
            ['Link', self.link],
            ['Tags', ', '.join(self.tags)],
            ['Date-Time', self.date_published]
        ],
            headers=['#', self.article_id],
            tablefmt='plain')

    def set_tags_and_date(self):
        """
        Receives a url to an article.
        Retrieves the url source code as html.
        Scrapes and returns the articles topic tags and datetime of publication.
        :param article_link: str
        :return: list of strings
        """
        article_link = self.link
        sub_r = requests.get(article_link)
        sub_soup = BeautifulSoup(sub_r.content, 'html.parser')
        tags_tag = sub_soup.find('div', class_='tags')
        self.tags = [tag.get_text() for tag in tags_tag.find_all('a')]
        self.date_published = sub_soup.find('time').get('datetime')

    def get_link(self):
        """Returns url (str) to article webpage"""
        return self.link

    def get_article_id(self):
        """Returns article id (int)"""
        return self.article_id


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
    coindesk_reader.add_argument('num_articles', type=float, metavar='num_articles',
                                 help=f'Number of articles, from 1 to {MAX_ARTICLES}',
                                 choices=list(range(1, MAX_ARTICLES + 1)))
    args = coindesk_reader.parse_args()
    section = args.section
    num_articles = int(args.num_articles)

    return section_dict[section], num_articles


def get_html(url, num_articles):
    """Receives the url to coindesk.com.
    Opens the url using Chrome driver.
    Clicks on the 'MORE' button several times.
    Returns the page source code as html,"""
    browser = webdriver.Chrome()
    browser.get(url)
    scrolls = (num_articles - ARTICLES_PER_HOME) // ARTICLES_PER_PAGE + 1
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


def parse_article_html(html):
    """
    Parses each article html from main url html.
    :param html: the main page html (str)
    :return: list of html strings for each article
    """
    soup = BeautifulSoup(html, 'html.parser')
    return [article_html for article_html in soup.find_all('div', class_='text-content')]


def insert_data(article, host, user, password, database):
    with pymysql.connect(host=host, user=user, password=password, database=database,
                         cursorclass=pymysql.cursors.DictCursor) as connection_instance:
        with connection_instance.cursor() as cursor:
            sql = f'''INSERT INTO {SUMMARIES_TABLE} (summary) 
                VALUES ("{article}")'''
            cursor.execute(sql)
            summary_id = cursor.lastrowid
            print(datetime.datetime.strptime(article.date_published,"%Y-%m-%dT%H:%M:%S"))
            sql = f'''INSERT INTO {ARTICLES_TABLE} (title,summary_id,publication_date,url)
                VALUES ("{article.name}",
                {summary_id},
                {datetime.datetime.strptime(article.date_published,"%Y-%m-%dT%H:%M:%S")},
                {article.link})'''
            cursor.execute(sql)
            article_id = cursor.lastrowid
            for author in article.author:
                cursor.execute(f'SELECT id FROM {AUTHORS_TABLE} WHERE name = {author}')
                print(cursor.fetchone())
            sql = f'DELETE FROM {SUMMARIES_TABLE}'
            cursor.execute(sql)
    # article_sql = [f"""INSERT INTO {ARTICLES_TABLE} (title, publication_date, url, category_id, summary_id)
    # """]


def main():
    """Receives Coindesk topic section and number of articles to print as command parameters.
    Uses selenium to retrieve the required html script.
    Scrapes and prints each article for the following data:
        Title, Summary, Author, Link, Tags and Date-Time"""
    section, num_arts = welcome()
    html = get_html(URL + section, num_arts)
    article_html_list = parse_article_html(html)
    articles = [Article(article_html) for article_html in tqdm.tqdm(article_html_list)]
    # for article in articles:
    #     # article.set_tags_and_date(article.get_link())
    #     print(article, "\n")
    #     if article.get_article_id() == num_arts:
    #         break
    insert_data(articles[0],HOST,USER,'Dungeon!995',DATABASE)


if __name__ == '__main__':
    main()
