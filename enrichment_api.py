import grequests
import requests
from datetime import datetime
from config import *
from Coindesk_Scraper import Article


def enrich_tag(tag, num_article=100, from_date=None, to_date=None, domains=None, sort_by='publishedAt'):
    """
    uses news api to retrieve articles of a certain tag
    :param tag: tag to search
    :param num_article: number of articles [max: 100 blocked by api]
    :param from_date: earliest date to search
    :param to_date: latest date to search
    :param domains: domains to search in
    :param sort_by: sort articles by [publishedAt = latest, popularity = from popular sources,
    relevancy = most relevant to tag]
    :return: list of articles
    """
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
    url = f'https://newsapi.org/v2/everything?q={tag}&pageSize={num_article}&language=en&excludeDomains=coindesk.com&apiKey={API_KEY}' \
          f'{sort_by_str}{from_date_str}{to_date_str}{domains_str}'
    response = requests.get(url)
    json = response.json()
    articles = []
    for article in json[ENRICHMENT_ARTICLES]:
        if article[ENRICHMENT_AUTHOR] is None:
            article[ENRICHMENT_AUTHOR] = 'Unknown'
        if article[ENRICHMENT_DESCRIPTION] is None:
            article[ENRICHMENT_DESCRIPTION] = ''
        articles.append(Article(article[ENRICHMENT_TITLE], article[ENRICHMENT_DESCRIPTION],
                                [article[ENRICHMENT_AUTHOR]], article[ENRICHMENT_URL], [tag],
                                datetime.strptime(article[ENRICHMENT_PUBLISH_DATE], API_DATE_FORMAT),
                                [ENRICHMENT_CATEGORY], article[ENRICHMENT_SOURCE][ENRICHMENT_SOURCE_NAME]))
    return articles
