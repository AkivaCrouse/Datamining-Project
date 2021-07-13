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
import selenium.common.exceptions

from config import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from tabulate import tabulate
from datetime import datetime
from datetime import date
from datetime import timedelta


class Article:
    """
        A class to represent an article.

        Attributes
        ----------
        article_num : int
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
        categories: (str)
            Categories article falls under.


        Methods
        -------
        get_article_num():
            Returns article number of instance created.

        get_title(self):
            Returns article title

        get_summary(self):
            Returns article summary

        get_link(self):
            Returns URL to article page

        get_tags(self):
            Returns article tags

        get_date_published(self):
            Returns date and time article was published

        get_categories(self):
            Returns article category

        get_authors(self):
            Returns article author(s)
        """
    article_num = 0

    def __init__(self, title, summary, author, link, tags, date_published, categories):
        """
        Constructs all necessary attributes of the vehicle object.
        """
        Article.article_num += 1
        self.article_num = Article.article_num
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
            headers=['#', self.article_num],
            tablefmt='plain')

    def get_article_num(self):
        """:return: article number (int)"""
        return self.article_num

    def get_title(self):
        """:return: article title (str)"""
        return self.title

    def get_summary(self):
        """:return: article summary"""
        return self.summary

    def get_link(self):
        """:return: url (str) to article webpage"""
        return self.link

    def get_tags(self):
        """:return: article tags (list)"""
        return self.tags

    def get_date_published(self):
        """:return: date and time article was published."""
        return self.date_published

    def get_categories(self):
        """:return: the categories the article belongs to"""
        return self.categories

    def get_authors(self):
        """:return: the authors that wrote the article"""
        return self.author


# Overriding error function in order to display the help message
# whenever the error method is triggered - UX purposes.
class MyParser(argparse.ArgumentParser):
    """
    Overriding the 'error' function in ArgumentParser in order to display the help message
    whenever the error method is triggered, for UX purposes.
    """

    def error(self, message):
        """
        overridden error function
        :param message: message to present to user
        """
        sys.stderr.write('error: %s\n' % message)
        coin_logger.error(message)
        self.print_help()
        sys.exit(2)


def welcome():
    """
    Gets the category and number of articles required by the user, with argparser,
    and outputs the relevant URL suffix for these articles together with the number of articles.
    the program also response to the flag -h for help.
    return:    category: relevant category URL suffix.
               scrape_by: number of articles requested by the user
               username: username for mysql
               password: password for mysql
               host: url of database server
               database: database that the program is going to save the data to
    """

    category_dict = {
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
    coindesk_reader.add_argument('category', type=str.lower, metavar='category',
                                 help='Choose one of the following categories: '
                                      'latest, tech, business, regulation, people, '
                                      'features, opinion, markets.',
                                 choices=['latest', 'tech', 'business', 'regulation', 'people', 'opinion', 'markets'])
    date_or_num.add_argument('-num', type=int, metavar='num_articles',
                             help=f'You can choose one of the two options: -num or -date.'
                                  f'\nChoose number of articles, from 1 to {MAX_ARTICLES} '
                                  f'in "-num [your number]" format.',
                             choices=list(range(1, MAX_ARTICLES + 1)))
    date_or_num.add_argument('-date', type=lambda s: datetime.strptime(s, '%Y-%m-%d'), metavar='from_date',
                             help=f'You can choose one of the two options: -num or -date. '
                                  f' Enter Date in "-date YYYY-MM-DD" format. '
                                  f'You will get articles published after that date')
    coindesk_reader.add_argument('-u', '--username', help='username of mysql', default=USER)
    required = coindesk_reader.add_argument_group('required arguments')
    required.add_argument('-p', '--password', help='password of mysql', required=True)
    coindesk_reader.add_argument('-host', help='url of database server', default=HOST)
    coindesk_reader.add_argument('-db', '--database', help='Name of database to insert to', default=DATABASE)

    args = coindesk_reader.parse_args()
    category = args.category
    scrape_by = {}
    if args.num is not None:
        scrape_by[SCRAPE_BY_TYPE] = NUM_SCRAPE_TYPE
        scrape_by[SCRAPE_BY_FUNCTION] = by_number_of_articles
        scrape_by[SCRAPE_BY_PARAMETERS] = int(args.num)

    from_date = args.date
    # Validating date is not too far back nor in the future
    if from_date is not None:
        now = datetime.today()
        if from_date > now:
            coindesk_reader.error("The date is the future, please enter another date")
        if abs((from_date - now).days) > 365:
            coindesk_reader.error("The date you entered is too far back, please enter a date within the last 365 days")
        scrape_by[SCRAPE_BY_TYPE] = DATE_SCRAPE_TYPE
        scrape_by[SCRAPE_BY_FUNCTION] = by_date_of_articles
        scrape_by[SCRAPE_BY_PARAMETERS] = from_date

    return category_dict[category], scrape_by, args.username, args.password, args.host, args.database


def by_number_of_articles(num_articles, browser):
    """
    opens the webpage by the number of articles needed
    :param num_articles: number of articles
    :param browser: browser driver
    """
    num_elements = 0
    while num_elements < num_articles:
        num_elements = len(browser.find_elements_by_class_name("text-content"))
        try:
            more_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cta-story-stack")))
        except TimeoutException:
            print("Articles did not load in time due to network.")
            coin_logger.error("Articles did not load in time due to network.")
            browser.close()
            sys.exit(1)
        more_button.click()
        time.sleep(1)


def by_date_of_articles(from_date, browser):
    """
    opens the webpage by the dates of the articles
    :param from_date: date limit to scrape to
    :param browser: browser driver
    """
    page_time = datetime.today()
    while page_time > from_date:
        date_published_text = browser.find_elements_by_class_name("time")[-1].text
        if date_published_text.startswith(TODAY) or date_published_text[0].isdigit():
            date_published_text = datetime.today().strftime(date_format)
        elif date_published_text.startswith(YESTERDAY):
            today = date.today()
            date_published_text = (today - timedelta(days=1)).strftime(date_format)
        page_time = datetime.strptime(date_published_text, date_format)
        try:
            more_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cta-story-stack")))
        except TimeoutException:
            print("Articles did not load in time due to network.")
            coin_logger.error("Articles did not load in time due to network.")
            browser.close()
            sys.exit(1)
        more_button.click()
        time.sleep(1)


def get_html(url, scrape_by):
    """
    Opens the url using Chrome driver.
    Clicks on the 'MORE' button several times.
    :param url: coindesk.com url
    :param scrape_by: dictionary that details how to scrape
    :return: the page source code as html
    """
    browser = webdriver.Chrome()
    try:
        browser.get(url)
        scrape_by[SCRAPE_BY_FUNCTION](scrape_by[SCRAPE_BY_PARAMETERS], browser)
    except selenium.common.exceptions.WebDriverException as err:
        print(err.msg)
        coin_logger.error(err.msg)
        exit(1)
    html = browser.page_source
    return html


def scrape_main(html):
    """
    Receives the full html from the main page and returns a list of urls to all the articles.
    :param html: str
    :return: list
    """
    soup = BeautifulSoup(html, 'html.parser').find('div', class_='story-stack')
    links = pd.Series(
        [URL + link.get('href') for link in soup.find_all('a', title=True)
         if str(link.get('href')).count("/") == 1]).unique()
    coin_logger.info('Scraped article urls from main page.')
    return links


def scrape_articles(urls):
    """
    scraps all of the articles from the url list
    :param urls: list of urls
    :return: lists of article data
    """
    responses = grequests.map((grequests.get(url) for url in urls))
    soups = [BeautifulSoup(response.content, 'html.parser') for response in responses]
    data_dicts = []
    # TODO: find better way to check for 404s?
    for soup in soups:
        props = json.loads(soup.find(SCRIPT_TAG, id=SCRIPT_ID, type=SCRIPT_TYPE).string)[PROPERTIES_TAG][
            INITIAL_PROPERTIES_TAG][PAGE_PROPERTIES]
        if DATA_TAG not in props:  # article doesn't exist anymore (404 page)
            coin_logger.warning('Encountered link that led to an internal 404 will not scrap its data.')
            continue
        else:
            data_dicts.append(props[DATA_TAG])

    titles = [data[TITLE_TAG] for data in data_dicts]
    summaries = [data[SUMMARY_TAG] for data in data_dicts]
    authors = [[author[AUTHOR_NAME_TAG] for author in data[AUTHORS_TAG]] for data in data_dicts]
    tags = [[tag[TAG_NAME_TAG] for tag in data[TAGS_TAG]] for data in data_dicts]
    times_published = [datetime.strptime(data[PUBLISHED_DATE_TAG], PUBLISHED_DATE_FORMAT) for data in data_dicts]
    categories = [data[TAXONOMY_TAG][CATEGORY_TAG] for data in data_dicts]
    return titles, summaries, authors, tags, times_published, categories


def scraper(html, batch, scrape_by, user, password, host, database):
    """
    scrapes the html source code and save the data into the database in batches
    :param html: string of html source code
    :param batch: int size of batch
    :param scrape_by: dictionary defining how to scrape
    :param user: username of mysql
    :param password: password of mysql
    :param host: url of database server
    :param database: database to save to
    :return:
    """
    links = scrape_main(html)
    links = list(split_list(links, batch))

    for set_number, link_set in enumerate(links):
        articles = []
        titles, summaries, authors, tags, times_published, categories = scrape_articles(link_set)
        coin_logger.info('Scraped article batch from their pages')
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
            if stop_condition(new_article, scrape_by):
                insert_batch(articles, batch, host, user, password, database)
                coin_logger.info('Finished scraping and saved data to database.')
                return
            print(new_article, '\n')
            articles.append(new_article)
        insert_batch(articles, batch, host, user, password, database)
    coin_logger.info('Finished scraping and saved data to database.')


def split_list(lst, n):
    """
    Yields a generator with lists of n sizes chunks and a remainder if necessary
    :param lst: list
    :param n: int
    :return:
    """
    """Yields a generator with lists of n sizes chunks and a remainder if necessary"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def stop_condition(article, scrape_by):
    """
    stop condition for the loop of the scraping (because the html code has more articles than needed)
    :param article: current article
    :param scrape_by: dictionary defining how to scrape by
    :return: boolean
    """
    if scrape_by[SCRAPE_BY_TYPE] == DATE_SCRAPE_TYPE:
        return article.get_date_published() <= scrape_by[SCRAPE_BY_PARAMETERS]
    if scrape_by[SCRAPE_BY_TYPE] == NUM_SCRAPE_TYPE:
        return article.get_article_num() >= scrape_by[SCRAPE_BY_PARAMETERS]
    return False


def insert_batch(articles, batch_size, host, user, password, database):
    """
    insert into database a batch of articles
    :param articles: list of articles
    :param batch_size: int batch size (isn't really needed because the list is going to be batch size)
    :param host: url of database server
    :param user: username of mysql
    :param password: password of mysql
    :param database: database to save to
    :return:
    """
    try:
        with pymysql.connect(host=host, user=user, password=password, database=database,
                             cursorclass=pymysql.cursors.DictCursor) as connection_instance:
            count = 0
            for a in articles:
                if insert_data(a, connection_instance):
                    count += 1
                if count == batch_size:
                    connection_instance.commit()
                    count = 0
            connection_instance.commit()
            coin_logger.info('Finished saving data batch to database')
    except pymysql.err.Error as err:
        print(err.args)
        coin_logger.error(err.args)
        exit(1)


def insert_data_to_entity_table(sql, data, cursor, log_msg):
    cursor.execute(sql, data)
    coin_logger.info(log_msg)
    return cursor.lastrowid


def insert_many_to_many_entities(create_single_sql, find_sql, create_relationship_sql, entity_pk_name, partner_pk, data,
                                 cursor, log_msg, log_single_entity, debug_msg):
    for data_point in data:
        cursor.execute(find_sql, [data_point])
        result = cursor.fetchone()
        if result is None:
            cursor.execute(create_single_sql, [data_point])
            coin_logger.info(log_single_entity)
            data_point_id = cursor.lastrowid
        else:
            data_point_id = result[entity_pk_name]
            coin_logger.debug(debug_msg)
        cursor.execute(create_relationship_sql, [partner_pk, data_point_id])
        coin_logger.info(log_msg)


def insert_data(article, conn):
    """
    save article to database
    :param article: article to save
    :param conn: connection object
    :return: boolean if inserted new data
    """
    try:
        with conn.cursor() as cursor:
            summary_id = insert_data_to_entity_table(INSERT_INTO_SUMMARIES,
                                                     article.get_summary(), cursor, 'Saved summary to database.')
            article_id = insert_data_to_entity_table(INSERT_INTO_ARTICLES,
                                                     [article.get_title(), summary_id, article.get_date_published(),
                                                      article.get_link()],
                                                     cursor, 'Saved article to database.')

            insert_many_to_many_entities(INSERT_INTO_AUTHORS, FIND_AUTHOR, INSERT_INTO_RELATIONSHIP_ARTICLE_AUTHOR,
                                         AUTHOR_ID, article_id, article.get_authors(), cursor,
                                         'Saved author-article relationship to database.',
                                         'Saved author to database.',
                                         'Author exists already in database.')

            insert_many_to_many_entities(INSERT_INTO_TAGS, FIND_TAG, INSERT_INTO_RELATIONSHIP_ARTICLE_TAG,
                                         TAG_ID, article_id, article.get_tags(), cursor,
                                         'Saved tag-article relationship to database.',
                                         'Saved tag to database.',
                                         'Tag exists already in database.')

            insert_many_to_many_entities(INSERT_INTO_CATEGORY, FIND_CATEGORY, INSERT_INTO_RELATIONSHIP_ARTICLE_CATEGORY,
                                         CATEGORY_ID, article_id, article.get_categories(), cursor,
                                         'Saved category-article relationship to database.',
                                         'Saved category to database.',
                                         'Category exists already in database.')
        return True
    except pymysql.err.IntegrityError:
        coin_logger.warning(f'Duplicate data, will skip this article: {article.get_link()}.')
        return False


def main():
    """Receives Coindesk topic category and number of articles to print as command parameters.
    Uses selenium to retrieve the required html script.
    Scrapes and prints each article for the following data:
        Title, Summary, Author, Link, Tags and Date-Time"""
    before = time.time()
    category, scrap_by, username, password, host, database = welcome()
    html = get_html(URL + category, scrap_by)
    scraper(html, BATCH, scrap_by, username, password, host, database)
    after = time.time()
    print(f"\nScraping took {round(after - before, 3)} seconds.")


if __name__ == '__main__':
    main()
