import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import keys


PATH = "C:\Program Files (x86)\chromedriver.exe"
ARTICLE_LINK_INDEX = 1
WEB_PAGE_HOME = "https://www.coindesk.com"
URL="https://www.coindesk.com/category/tech"
MORE_CLICKS = 3


def get_html(url):
    """Receives the url to coindesk.com.
    Opens the url using Chrome driver.
    Clicks on the 'MORE' button several times.
    Returns the page source code as html,"""
    browser = webdriver.Chrome(PATH)
    browser.get(url)
    for click_more in range(MORE_CLICKS):
        more_button = browser.find_element_by_class_name('cta-story-stack')
        more_button.click()
        time.sleep(3)
    html = browser.page_source
    # browser.close()
    return html


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


def scrape(html):
    soup = BeautifulSoup(html, 'html.parser')
    counter = 0
    for article in soup.find_all('div', class_='text-content'):
        heading = article.h4.text
        authors = [author.get_text() for author in article.find_all('span', class_='credit')]  # may have multiple Authors
        date_and_time = article.time.text
        summary = article.p.text

        links = [link.get('href') for link in article.find_all('a')]
        article_link = WEB_PAGE_HOME + links[ARTICLE_LINK_INDEX]
        tags = get_tags(article_link)
        print("Heading:", heading)
        print("Summary: ", summary)
        print("Author:", authors)
        print("Link:", article_link)
        print("Tags:", tags)
        print("Time: ", date_and_time)
        counter += 1
        print("Count:", counter)
        print()


def main():
    html = get_html(URL)
    scrape(html)


if __name__ == '__main__':
    main()