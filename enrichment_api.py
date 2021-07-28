import grequests
import requests
import json
from datetime import datetime
from config import *
from Coindesk_Scraper import Article


def enrich_tag(tag, num_article, from_date=None, to_date=None, domains=None, sort_by='publishedAt'):
    from_date_str = ''
    to_date_str = ''
    domains_str = ''
    sort_by_str = f'&sortBy={sort_by}'
    if from_date is not None:
        from_date_str = f'&from={from_date}'
    if to_date is not None:
        to_date_str = f'&to={to_date}'
    if domains is not None:
        domains_str = f'&domains={",".join(domains)}'

    url = f'https://newsapi.org/v2/everything?q={tag}&language=en&excludeDomains=coindesk.com&apiKey={API_KEY}' \
          f'{sort_by_str}{from_date_str}{to_date_str}{domains_str}'
    response = requests.get(url)
    response_json = response.json()
    articles = []
    for article in response_json['articles']:
        articles.append(Article(article['title'], article['description'], article['author'], article['url'],
                                tag, datetime.strptime(article['publishedAt'], API_DATE_FORMAT), 'Enriched data'))

    return articles
