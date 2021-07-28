import grequests
import requests
from datetime import datetime
from config import *
from Coindesk_Scraper import Article


def validate_params(num_article, from_date=None, to_date=None, domains=None, sort_by='publishedAt'):
    """
    validates the parameters for the enrichment api
    :param num_article: number of articles [max: 100 blocked by api]
    :param from_date: earliest date to search in iso format
    :param to_date: latest date to search in iso format
    :param domains: list of domains to search in
    :param sort_by: sort articles by [publishedAt = latest, popularity = from popular sources,
    relevancy = most relevant to tag]
    :return: num_article, from_date_str, to_date_str, domains_str, sort_by_str
    """
    from_date_str = ''
    to_date_str = ''
    domains_str = ''
    if sort_by not in SORT_BY_OPTIONS:
        raise ValueError(f'sortBy must be one of these values: {SORT_BY_OPTIONS}')
    sort_by_str = f'&sortBy={sort_by}'
    if num_article > 100 or num_article <= 0:
        raise ValueError('Free usage of news api needs a number between 1 - 100')
    try:
        datetime.strptime(from_date, PUBLISHED_DATE_FORMAT)
        datetime.strptime(to_date, PUBLISHED_DATE_FORMAT)
    except ValueError:
        raise ValueError(f"Incorrect data format, should be {PUBLISHED_DATE_FORMAT}")
    if from_date is not None:
        from_date_str = f'&from={from_date}'
    if to_date is not None:
        to_date_str = f'&to={to_date}'
    if domains is not None:
        domains_str = f'&domains={",".join(domains)}'
    return num_article, from_date_str, to_date_str, domains_str, sort_by_str


def enrich_tag(tag, num_article=100, from_date=None, to_date=None, domains=None, sort_by='publishedAt'):
    """
    uses news api to retrieve articles of a certain tag
    :param tag: tag to search
    :param num_article: number of articles [max: 100 blocked by api]
    :param from_date: earliest date to search in iso format
    :param to_date: latest date to search in iso format
    :param domains: list of domains to search in
    :param sort_by: sort articles by [publishedAt = latest, popularity = from popular sources,
    relevancy = most relevant to tag]
    :return: list of articles
    """
    try:
        num_article, from_date_str, to_date_str, domains_str, sort_by_str = validate_params(num_article, from_date, to_date,
                                                                                            domains, sort_by)
        url = f'https://newsapi.org/v2/everything?q={tag}&pageSize={num_article}&language=en&excludeDomains=coindesk.com&apiKey={API_KEY}' \
              f'{sort_by_str}{from_date_str}{to_date_str}{domains_str}'
        response = requests.get(url)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        enrichment_logger.info('Used enrichment api to retrieve more articles')
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
    except ValueError as ve:
        print(ve.args)
        enrichment_logger.error(ve.args)
        exit(1)
    except requests.exceptions.RequestException as re:
        print(re.args)
        enrichment_logger.error(re.args)
        exit(1)
