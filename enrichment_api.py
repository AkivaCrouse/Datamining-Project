import grequests
import requests
from datetime import datetime
from config import *
from Coindesk_Scraper import Article


def enrich_tag(tag, num_article, from_date=None, to_date=None, domains=None, sort_by='publishedAt'):
    pages = (num_article // 100) + (num_article % 100 > 0)
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
    responses = grequests.map((grequests.get(url+f'&page={i}') for i in range(1, pages + 1)))
    responses_json = [response.json() for response in responses]
    articles = []
    for json in responses_json:
        for article in json['articles']:
            if article['author'] is None:
                article['author'] = 'Unknown'
            articles.append(Article(article['title'], article['description'], [article['author']], article['url'],
                                    [tag], datetime.strptime(article['publishedAt'], API_DATE_FORMAT), ['Enriched data']))
    return articles

