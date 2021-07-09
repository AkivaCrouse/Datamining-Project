######################################################################################################################
"""
Title: Coindesk.com Scraper
Authors: Akiva Crouse & Ohad Ben Tzvi
Date: 23/06/2021
"""
######################################################################################################################


import argparse
import json
import sys
import textwrap as tw
import pandas as pd
import grequests
import time
import datetime

import pymysql

from config import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate
from datetime import datetime
from datetime import date
from datetime import timedelta


class Article:
    """
        A class to represent an article.

        Attributes
        ----------
        article_id : int
            Number article instance created.
        title: str
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
    article_id = 0  # TODO change article_id to article_num

    def __init__(self, title, summary, author, link, tags, date_published, categories):
        """
        Constructs all necessary attributes of the vehicle object.
        :param article_html: article related html parsed from the main html.
        """
        Article.article_id += 1
        self.article_id = Article.article_id
        self.title = title
        self.summary = summary
        self.author = author
        self.link = link
        self.tags = tags
        self.date_published = date_published
        self.categories = categories

    def __str__(self):
        """
        Constructs a table when print is called on the article.
        :return: table
        """
        return tabulate(tabular_data=[
            ['Title', self.title],
            ['Summary', '\n'.join(tw.wrap(self.summary, width=90))],
            ['Author', ', '.join(self.author)],
            ['Categories', ', '.join(self.categories)],
            ['Link', self.link],
            ['Tags', ', '.join(self.tags)],
            ['Date/Time Published', self.date_published]
        ],
            headers=['#', self.article_id],
            tablefmt='plain')

    def get_article_id(self):
        """Returns article id (int)"""
        return self.article_id

    def get_title(self):
        """Returns article title (str)"""
        return self.title

    def get_summary(self):
        """Returns article summary"""
        return self.summary

    def get_link(self):
        """Returns url (str) to article webpage"""
        return self.link

    def get_tags(self):
        """Returns article tags (list)"""
        return self.tags

    def get_date_published(self):
        """Returns date and time article was published."""
        return self.date_published

    def get_categories(self):
        """Returns the categories the article belongs to"""
        return self.categories

    def get_authors(self):
        """Returns the authors that wrote the article"""
        return self.author


# Overriding error function in order to display the help message
# whenever the error method is triggered - UX purposes.
class MyParser(argparse.ArgumentParser):
    """
    Overriding the 'error' function in ArgumentParser in order to display the help message
    whenever the error method is triggered, for UX purposes.
    """

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def welcome():
    """
    Gets the section and number of articles required by the user, with argparser,
    and outputs the relevant URL suffix for these articles together with the number of articles.
    the program also response to the flag -h for help.
    return:    section: relevant section URL suffix.
               num_articles: number of articles requested by the user
    """

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
    date_or_num = coindesk_reader.add_mutually_exclusive_group(required=True)
    coindesk_reader.add_argument('section', type=str.lower, metavar='section',
                                 help='Choose one of the following sections: latest, tech, business, regulation, people, '
                                      'features, opinion, markets.',
                                 choices=['latest', 'tech', 'business', 'regulation', 'people', 'opinion', 'markets'])
    date_or_num.add_argument('-num', type=float, metavar='num_articles',
                             help=f'You can choose one of the two options: -num or -date.'
                                  f'\nChoose number of articles, from 1 to {MAX_ARTICLES} '
                                  f'in "-num [your number]" format.',
                             choices=list(range(1, MAX_ARTICLES + 1)))
    date_or_num.add_argument('-date', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), metavar='from_date',
                             help=f'You can choose one of the two options: -num or -date. '
                                  f' Enter Date in "-date YYYY-MM-DD" format. '
                                  f'You will get articles published after that date')

    args = coindesk_reader.parse_args()
    print(args)
    section = args.section

    num_articles = int(args.num) if (args.num is not None) else args.num
    from_date = args.date

    # Validating date is not too far back nor in the future
    if from_date is not None:
        now = datetime.today()
        if from_date > now:
            coindesk_reader.error("The date is the future, please enter another date")
        if abs((from_date - now).days) > 365:
            coindesk_reader.error("The date you entered is too far back, please enter a date within the last 365 days")

    return section_dict[section], num_articles, section, from_date


def get_html(url, num_articles, from_date):
    """Receives the url to coindesk.com.
    Opens the url using Chrome driver.
    Clicks on the 'MORE' button several times.
    Returns the page source code as html,"""
    browser = webdriver.Chrome()
    browser.get(url)

    # TODO: maybe add dictionary parameter to split into more sub functions so this function will be more flexible
    if from_date is None:
        num_elements = 0
        while num_elements < num_articles:
            num_elements = len(browser.find_elements_by_class_name("text-content"))
            try:
                more_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cta-story-stack")))
            except Exception:  # TODO make this exception not so general.
                print("Articles did not load in time due to network.")
                browser.close()
                sys.exit(1)
            more_button.click()
            time.sleep(1)

    else:
        page_time = datetime.today()
        while page_time > from_date:
            date_published_text = browser.find_elements_by_class_name("time")[-1].text
            if date_published_text.startswith('Today') or date_published_text[0].isdigit():
                date_published_text = datetime.today().strftime('%b %d, %Y')
            elif date_published_text.startswith('Yesterday'):
                today = date.today()
                date_published_text = (today - timedelta(days=1)).strftime('%b %d, %Y')
            page_time = datetime.strptime(date_published_text, '%b %d, %Y')
            try:
                more_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cta-story-stack")))
            except Exception:  # TODO make this exception not so general.
                print("Articles did not load in time due to network.")
                browser.close()
                sys.exit(1)
            more_button.click()
            time.sleep(1)

    html = browser.page_source
    return html


def scrape_main(html):
    """
    Receives the full html from the main page and returns a list of urls to all the articles.
    :param html: str
    :return: list
    """
    soup = BeautifulSoup(html, 'html.parser').find('div', class_='story-stack')
    # print(soup.prettify())
    links = pd.Series(
        [URL + link.get('href') for link in soup.find_all('a', title=True)
         if str(link.get('href')).count("/") == 1]).unique()
    return links


def scrape_articles(urls):  # TODO Add doc strings
    # TODO: convert hardcoded strings to constants
    responses = grequests.map((grequests.get(url) for url in urls))
    soups = [BeautifulSoup(response.content, 'html.parser') for response in responses]
    data_dicts = []
    # TODO: find better way to check for 404s?
    for soup in soups:
        data = json.loads(soup.find('script', id='__NEXT_DATA__', type='application/json')
                          .string)['props']['initialProps']['pageProps']
        if 'data' not in data:  # article doesn't exist anymore (404 page)
            continue
        else:
            data_dicts.append(data['data'])

    titles = [data['headline'] for data in data_dicts]
    summaries = [data['excerpt'] for data in data_dicts]
    authors = [[author['name'] for author in data['authors']] for data in data_dicts]
    tags = [[tag['name'] for tag in data['tags']] for data in data_dicts]
    times_published = [datetime.strptime(data['published'], '%Y-%m-%dT%H:%M:%S') for data in data_dicts]
    categories = [data['taxonomy']['category'] for data in data_dicts]
    return titles, summaries, authors, tags, times_published, categories


def scraper(html, batch, num_arts, from_date, host, user, password, database):  # TODO Add doc strings
    links = scrape_main(html)
    links = list(split_list(links, batch))

    for set_number, link_set in enumerate(links):
        articles = []
        titles, summaries, authors, tags, times_published, categories = scrape_articles(link_set)

        for art_number in range(len(authors)):
            new_article = Article(
                title=titles[art_number],
                summary=summaries[art_number],
                author=authors[art_number],
                link=links[set_number][art_number],
                tags=tags[art_number],
                date_published=times_published[art_number],
                categories=categories[art_number]
            )
            if from_date is not None and new_article.get_date_published() <= from_date:
                insert_batch(articles, batch, host, user, password, database)
                return

            elif from_date is None and new_article.get_article_id() >= num_arts:
                insert_batch(articles, batch, host, user, password, database)
                return
            print(new_article, '\n')
            articles.append(new_article)
        insert_batch(articles, batch, host, user, password, database)


def split_list(lst, n):
    """Yields a generator with lists of n sizes chunks and a remainder if necessary"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def insert_batch(articles, batch_size, host, user, password, database):  # TODO: docstrings
    with pymysql.connect(host=host, user=user, password=password, database=database,
                         cursorclass=pymysql.cursors.DictCursor) as connection_instance:
        count = 0
        for a in articles:
            insert_data(a, connection_instance)
            count += 1
            if count == batch_size:
                connection_instance.commit()
                count = 0
        connection_instance.commit()


def insert_data(article, conn):  # TODO: docstrings
    # TODO: clean hardcoded strings and convert to constants, maybe find a way to reduce size of function
    with conn.cursor() as cursor:
        sql = f'''INSERT INTO {SUMMARIES_TABLE} (summary) 
            VALUES (%s)'''
        cursor.execute(sql, article.get_summary())
        summary_id = cursor.lastrowid
        sql = f'''INSERT INTO {ARTICLES_TABLE} (title,summary_id,publication_date,url)
            VALUES (%s, %s, %s, %s)'''
        cursor.execute(sql, [article.get_title(), summary_id, article.get_date_published(), article.get_link()])

        article_id = cursor.lastrowid
        for author in article.get_authors():
            cursor.execute(f'SELECT id FROM {AUTHORS_TABLE} WHERE name = "{author}"')
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f'INSERT INTO {AUTHORS_TABLE} (name) VALUES ("{author}")')
                author_id = cursor.lastrowid
            else:
                author_id = result['id']
            cursor.execute(f'INSERT INTO {AUTHORS_ARTICLES_TABLE} VALUES ({article_id},{author_id})')

        for tag in article.get_tags():
            cursor.execute(f'SELECT id FROM {TAGS_TABLE} WHERE name = "{tag}"')
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f'INSERT INTO {TAGS_TABLE} (name) VALUES ("{tag}")')
                tag_id = cursor.lastrowid
            else:
                tag_id = result['id']
            cursor.execute(f'INSERT INTO {TAGS_ARTICLES_TABLE} VALUES ({article_id},{tag_id})')

        for category in article.get_categories():
            cursor.execute(f'SELECT id FROM {CATEGORIES_TABLE} WHERE category = "{category}"')
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f'INSERT INTO {CATEGORIES_TABLE} (category) VALUES ("{category}")')
                category_id = cursor.lastrowid
            else:
                category_id = result['id']
            cursor.execute(f'INSERT INTO {CATEGORIES_ARTICLES_TABLE} VALUES ({article_id},{category_id})')


def main():
    """Receives Coindesk topic section and number of articles to print as command parameters.
    Uses selenium to retrieve the required html script.
    Scrapes and prints each article for the following data:
        Title, Summary, Author, Link, Tags and Date-Time"""
    before = time.time()
    section, num_arts, category, from_date = welcome()
    html = get_html(URL + section, num_arts, from_date)
    scraper(html, BATCH, num_arts, from_date, HOST, USER, 'Dungeon!995', DATABASE)
    after = time.time()
    print(f"\nScraping took {round(after - before, 3)} seconds.")


if __name__ == '__main__':
    main()
