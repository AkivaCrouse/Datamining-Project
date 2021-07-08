######################################################################################################################
"""
Title: Coindesk.com Scraper
Authors: Akiva Crouse & Ohad Ben Tzvi
Date: 23/06/2021
"""
######################################################################################################################


import argparse
import sys
import textwrap as tw
import pandas as pd
import grequests
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
from tqdm import tqdm


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
    article_id = 0 # TODO change article_id to article_num

    def __init__(self, title, summary, author, link, tags, date_published, category):
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
        self.category = category

    def __str__(self):
        """
        Constructs a table when print is called on the article.
        :return: table
        """
        return tabulate(tabular_data=[
            ['Title', self.title],
            ['Summary', '\n'.join(tw.wrap(self.summary, width=90))],
            ['Author', ', '.join(self.author)],
            ['Category', self.category],
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
    coindesk_reader.add_argument('section', type=str.lower, metavar='section',
                                 help='Choose one of the following sections: latest, tech, business, regulation, people, '
                                      'features, opinion, markets.',
                                 choices=['latest', 'tech', 'business', 'regulation', 'people', 'opinion', 'markets'])
    coindesk_reader.add_argument('num_articles', type=float, metavar='num_articles',
                                 help=f'Number of articles, from 1 to {MAX_ARTICLES}',
                                 choices=list(range(1, MAX_ARTICLES + 1)))
    coindesk_reader.add_argument('-date', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), metavar='from_date',
                                 help=f'Enter Date in "-date YYYY-MM-DD" format. '
                                      f'You will get articles published after that date')
    args = coindesk_reader.parse_args()
    section = args.section
    num_articles = int(args.num_articles)
    from_date = args.date
    # Validating date is not too far back nor in the future
    if from_date is not None:
        now = datetime.datetime.today()
        if from_date > now:
            coindesk_reader.error("The date is the future, please enter another date")
        if abs((from_date - now).days) > 365:
            coindesk_reader.error("The date you entered is too far back, please enter a date within the last 365 days")

    return section_dict[section], num_articles, section, from_date


def get_html(url, num_articles):
    """Receives the url to coindesk.com.
    Opens the url using Chrome driver.
    Clicks on the 'MORE' button several times.
    Returns the page source code as html,"""
    browser = webdriver.Chrome()
    browser.get(url)
    # scrolls = (num_articles - CFG.ARTICLES_PER_HOME) // CFG.ARTICLES_PER_PAGE + 1
    num_elements = 0
    while num_elements < num_articles: #TODO Add date condition.
    # for click_more in tqdm(range(scrolls)):
        num_elements = len(browser.find_elements_by_class_name("text-content"))
        try:
            more_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cta-story-stack")))

        except Exception: #TODO make this exception not so general.
            print("Articles did not load in time due to network.")
            browser.close()
            sys.exit(1)

        more_button.click()
        # time.sleep(CFG.SLEEPTIME)

    html = browser.page_source
    return html


def scrape_main(html):
    """
    Receives the full html from the main page and returns a list of urls to all the articles.
    :param html: str
    :return: list
    """
    soup = BeautifulSoup(html, 'html.parser').find('div', class_='story-stack')
    titles = [article_block.h4.get_text() for article_block in soup.find_all('div', class_="text-content")]
    summaries = [article_block.find('p', class_="card-text").get_text()
                 for article_block in soup.find_all('div', class_="text-content")]
    links = pd.Series(
        [CFG.URL + link.get('href') for link in soup.find_all('a', title=True)
         if str(link.get('href')).count("/") == 1]).unique()

    return titles, summaries, links


def scrape_articles(urls):  # TODO Add doc strings
    responses = grequests.map((grequests.get(url) for url in urls))
    soups = [BeautifulSoup(response.content, 'html.parser') for response in responses]
    authors = [[author.get_text() for author in soup.find('div', class_="article-hero-authors").find_all('h5')]
               for soup in soups]
    tags = [[tag.get_text() for tag in soup.find('div', class_='tags').find_all('a')] for soup in soups]
    times_published = [soup.find('time').get('datetime') for soup in soups]
    # titles = [soup.h1.get_text() for soup in soups]
    # summaries = [soup.find('div', class_="article-hero-blurb").p.get_text()
    #              if soup.find_all('div', class_="article-hero-blurb")
    #              else ""
    #              for soup in soups]
    # articles = [Article(titles[i],
    #                     summaries[i],
    #                     authors[i],
    #                     urls[i],
    #                     tags[i],
    #                     time_published[i]) for i in range(len(urls))]
    # for article in articles:
    #     print(article, '\n')
    return authors, tags, times_published


def scraper(html, batch, category, num_arts):  # TODO Add doc strings
    titles, summaries, links = scrape_main(html)

    titles = list(split_list(titles, batch))
    summaries = list(split_list(summaries, batch))
    links = list(split_list(links,batch))

    for set_number, link_set in enumerate(links):
        articles = []
        authors, tags, times_published = scrape_articles(link_set)
        for art_number in range(len(authors)):
            new_article = Article(
                                title=titles[set_number][art_number],
                                summary=summaries[set_number][art_number],
                                author=authors[art_number],
                                link=links[set_number][art_number],
                                tags=tags[art_number],
                                date_published=times_published[art_number],
                                category=category
                                )
            print(new_article, '\n')
            articles.append(new_article)
            # TODO: Roni add insert functionality here with your function.
            # TODO if you insert by single article at a time insert here.

            if new_article.get_article_id() >= num_arts: # TODO Add date condition.
            # TODO if you inserting by a list, insert here.

                return


def split_list(lst, n):
    """Yields a generator with lists of n sizes chunks and a remainder if necessary"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def insert_batch(articles, batch_size, host, user, password, database):
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


def insert_data(article, conn):
    with conn.cursor() as cursor:
        sql = f'''INSERT INTO {SUMMARIES_TABLE} (summary) 
            VALUES (%s)'''
        cursor.execute(sql, article.summary)
        summary_id = cursor.lastrowid
        sql = f'''INSERT INTO {ARTICLES_TABLE} (title,summary_id,publication_date,url)
            VALUES (%s, %s, %s, %s)'''
        cursor.execute(sql, [article.name, summary_id,
                             datetime.datetime.strptime(article.date_published, "%Y-%m-%dT%H:%M:%S"), article.link])

        article_id = cursor.lastrowid
        for author in article.author:
            cursor.execute(f'SELECT id FROM {AUTHORS_TABLE} WHERE name = "{author}"')
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f'INSERT INTO {AUTHORS_TABLE} (name) VALUES ("{author}")')
                author_id = cursor.lastrowid
            else:
                author_id = result['id']
            cursor.execute(f'INSERT INTO {AUTHORS_ARTICLES_TABLE} VALUES ({article_id},{author_id})')

        for tag in article.tags:
            cursor.execute(f'SELECT id FROM {TAGS_TABLE} WHERE name = "{tag}"')
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f'INSERT INTO {TAGS_TABLE} (name) VALUES ("{tag}")')
                tag_id = cursor.lastrowid
            else:
                tag_id = result['id']
            cursor.execute(f'INSERT INTO {TAGS_ARTICLES_TABLE} VALUES ({article_id},{tag_id})')
    # cursor.execute(f'SELECT * FROM {ARTICLES_TABLE}')
    # print(pd.DataFrame(cursor.fetchall()), end='\n\n')
    # cursor.execute(f'SELECT * FROM {AUTHORS_TABLE}')
    # print(pd.DataFrame(cursor.fetchall()), end='\n\n')
    # cursor.execute(f'SELECT * FROM {AUTHORS_ARTICLES_TABLE}')
    # print(pd.DataFrame(cursor.fetchall()), end='\n\n')
    # cursor.execute(f'SELECT * FROM {TAGS_TABLE}')
    # print(pd.DataFrame(cursor.fetchall()), end='\n\n')
    # cursor.execute(f'SELECT * FROM {TAGS_ARTICLES_TABLE}')
    # print(pd.DataFrame(cursor.fetchall()), end='\n\n')
    # cursor.execute(f'SELECT * FROM {SUMMARIES_TABLE}')
    # print(pd.DataFrame(cursor.fetchall()), end='\n\n')


def main():
    """Receives Coindesk topic section and number of articles to print as command parameters.
    Uses selenium to retrieve the required html script.
    Scrapes and prints each article for the following data:
        Title, Summary, Author, Link, Tags and Date-Time"""
    before = time.time()
    section, num_arts, category = welcome()
    html = get_html(CFG.URL + section, num_arts)
    scraper(html, CFG.BATCH, category, num_arts)
    after = time.time()
    print(f"\nScraping took {round(after-before,3)} seconds.")


if __name__ == '__main__':
    main()