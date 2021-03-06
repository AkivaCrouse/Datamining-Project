import logging

# news_api constants
API_KEY = 'fece1de5cfde4f2d9d004ae04dcf8217'

# logging defaults
COIN_DESK_LOG_FILE = 'coindesk.log'
SQL_LOG_FILE = 'sql.log'
ENRICHMENT_API_LOG_FILE = 'enrichment_api.log'
coin_logger = logging.getLogger('articles')
coin_logger.setLevel(logging.INFO)
sql_logger = logging.getLogger('database-creation')
sql_logger.setLevel(logging.INFO)
enrichment_logger = logging.getLogger('enrich-api')
enrichment_logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')

# Coin Logger for log file
file_handler = logging.FileHandler(COIN_DESK_LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
coin_logger.addHandler(file_handler)

# SQL Logger for log file
file_handler = logging.FileHandler(SQL_LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
sql_logger.addHandler(file_handler)

# Enrichment Logger for log file
file_handler = logging.FileHandler(ENRICHMENT_API_LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
enrichment_logger.addHandler(file_handler)

# SQL defaults
HOST = 'localhost'
USER = 'root'
DATABASE = 'coindesk'
# Table names
ARTICLES_TABLE = 'articles'
AUTHORS_TABLE = 'authors'
SUMMARIES_TABLE = 'summaries'
TAGS_TABLE = 'tags'
CATEGORIES_TABLE = 'categories'
TAGS_ARTICLES_TABLE = 'tags_in_articles'
AUTHORS_ARTICLES_TABLE = 'authors_in_articles'
CATEGORIES_ARTICLES_TABLE = 'categories_in_articles'

# SQL Creation Scripts
CREATE_DATABASE = 'CREATE DATABASE IF NOT EXISTS '
USE_DATABASE = 'USE '
AUTHORS_CREATION = f"""CREATE TABLE IF NOT EXISTS {AUTHORS_TABLE} (id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(400) UNIQUE
            )
            """
SUMMARIES_CREATION = f"""CREATE TABLE IF NOT EXISTS {SUMMARIES_TABLE} (id INT AUTO_INCREMENT PRIMARY KEY,
            summary VARCHAR(400)  UNIQUE
            )
            """
CATEGORIES_CREATION = f"""CREATE TABLE IF NOT EXISTS {CATEGORIES_TABLE} (id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(100)
            )
            """
TAGS_CREATION = f"""CREATE TABLE IF NOT EXISTS {TAGS_TABLE} (id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100)
            )
            """
ARTICLES_CREATION = f"""CREATE TABLE IF NOT EXISTS {ARTICLES_TABLE} (id INT AUTO_INCREMENT PRIMARY KEY,
            title varchar(400),
            publication_date TIMESTAMP,
            url VARCHAR(300) UNIQUE,
            summary_id INT UNIQUE NOT NULL,
            source VARCHAR(100),
            FOREIGN KEY(summary_id) REFERENCES {SUMMARIES_TABLE}(id)
            )
            """
TAGS_ARTICLES_RELATIONSHIP_CREATION = f"""CREATE TABLE IF NOT EXISTS {TAGS_ARTICLES_TABLE} (
            article_id INT,
            tag_id INT,
            FOREIGN KEY(article_id) REFERENCES {ARTICLES_TABLE}(id),
            FOREIGN KEY(tag_id) REFERENCES {TAGS_TABLE}(id)
            )
            """
AUTHORS_ARTICLES_RELATIONSHIP_CREATION = f"""CREATE TABLE IF NOT EXISTS {AUTHORS_ARTICLES_TABLE} (
            article_id INT,
            author_id INT,
            FOREIGN KEY(article_id) REFERENCES {ARTICLES_TABLE}(id),
            FOREIGN KEY(author_id) REFERENCES {AUTHORS_TABLE}(id)
            )
            """
CATEGORIES_ARTICLES_RELATIONSHIP_CREATION = f"""CREATE TABLE IF NOT EXISTS {CATEGORIES_ARTICLES_TABLE} (
            article_id INT,
            category_id INT,
            FOREIGN KEY(article_id) REFERENCES {ARTICLES_TABLE}(id),
            FOREIGN KEY(category_id) REFERENCES {CATEGORIES_TABLE}(id)
            )
            """

# SQL INSERT scripts
INSERT_INTO_SUMMARIES = f'''INSERT INTO {SUMMARIES_TABLE} (summary) VALUES (%s)'''
INSERT_INTO_ARTICLES = f'''INSERT INTO {ARTICLES_TABLE} (title,summary_id,publication_date,url,source)
            VALUES (%s, %s, %s, %s, %s)'''
FIND_AUTHOR = f'SELECT id FROM {AUTHORS_TABLE} WHERE name = %s'
INSERT_INTO_AUTHORS = f'INSERT INTO {AUTHORS_TABLE} (name) VALUES (%s)'
INSERT_INTO_RELATIONSHIP_ARTICLE_AUTHOR = f'INSERT INTO {AUTHORS_ARTICLES_TABLE} VALUES (%s, %s)'
FIND_TAG = f'SELECT id FROM {TAGS_TABLE} WHERE name = %s'
INSERT_INTO_TAGS = f'INSERT INTO {TAGS_TABLE} (name) VALUES (%s)'
INSERT_INTO_RELATIONSHIP_ARTICLE_TAG = f'INSERT INTO {TAGS_ARTICLES_TABLE} VALUES (%s, %s)'
FIND_CATEGORY = f'SELECT id FROM {CATEGORIES_TABLE} WHERE category = %s'
INSERT_INTO_CATEGORY = f'INSERT INTO {CATEGORIES_TABLE} (category) VALUES (%s)'
INSERT_INTO_RELATIONSHIP_ARTICLE_CATEGORY = f'INSERT INTO {CATEGORIES_ARTICLES_TABLE} VALUES (%s, %s)'

# SQL QUERY scripts
TOP_TEN_TAGS = f"""
                    SELECT {TAGS_TABLE}.name as tag, COUNT(DISTINCT article_id) as tag_count
                    FROM {TAGS_TABLE} INNER JOIN {TAGS_ARTICLES_TABLE} ON {TAGS_ARTICLES_TABLE}.tag_id = {TAGS_TABLE}.id
                    INNER JOIN {ARTICLES_TABLE} ON {ARTICLES_TABLE}.id = {TAGS_ARTICLES_TABLE}.article_id
                    WHERE {ARTICLES_TABLE}.source = 'Coindesk'
                    GROUP BY {TAGS_TABLE}.name
                    ORDER BY tag_count DESC
                    LIMIT 10
                    """

# Table field names
AUTHOR_ID = 'id'
TAG_ID = 'id'
CATEGORY_ID = 'id'

# PATH = "C:\Program Files (x86)\chromedriver.exe"
PATH = '/home/roni/PycharmProjects/Datamining-Project/chromedriver'
ARTICLE_LINK_INDEX = 1
BATCH_SIZE = 10
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
BATCH = 10

# Scraping metadata tags
SCRIPT_TAG = 'script'
SCRIPT_ID = '__NEXT_DATA__'
SCRIPT_TYPE = 'application/json'
PROPERTIES_TAG = 'props'
INITIAL_PROPERTIES_TAG = 'initialProps'
PAGE_PROPERTIES = 'pageProps'
DATA_TAG = 'data'
TITLE_TAG = 'headline'
SUMMARY_TAG = 'excerpt'
AUTHORS_TAG = 'authors'
AUTHOR_NAME_TAG = 'name'
TAGS_TAG = 'tags'
TAG_NAME_TAG = 'name'
PUBLISHED_DATE_TAG = 'published'
PUBLISHED_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
CATEGORY_TAG = 'category'
TAXONOMY_TAG = 'taxonomy'

# Main date format constants
TODAY = 'Today'
YESTERDAY = 'Yesterday'
date_format = '%b %d, %Y'

# CLI scrape_by Constants
SCRAPE_BY_TYPE = 'type'
SCRAPE_BY_FUNCTION = 'function'
SCRAPE_BY_PARAMETERS = 'parameters'
NUM_SCRAPE_TYPE = 'num'
DATE_SCRAPE_TYPE = 'date'

# Enrichment api constants
BATCH_SIZE_ENRICH = 10
SORT_BY_OPTIONS = ['publishedAt', 'popularity', 'relevancy']
API_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
ENRICHMENT_ARTICLES = 'articles'
ENRICHMENT_AUTHOR = 'author'
ENRICHMENT_DESCRIPTION = 'description'
ENRICHMENT_TITLE = 'title'
ENRICHMENT_URL = 'url'
ENRICHMENT_PUBLISH_DATE = 'publishedAt'
ENRICHMENT_SOURCE = 'source'
ENRICHMENT_SOURCE_NAME = 'name'
ENRICHMENT_CATEGORY = 'Enriched data'
