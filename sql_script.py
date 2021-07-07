import pymysql
import argparse
import pandas as pd
from config import *

AUTHORS_TABLE = """CREATE TABLE IF NOT EXISTS Authors (id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(40)
            )
            """
SUMMARIES_TABLE = """CREATE TABLE IF NOT EXISTS Summaries (id INT AUTO_INCREMENT PRIMARY KEY,
            summary TEXT
            )
            """
CATEGORIES_TABLE = """CREATE TABLE IF NOT EXISTS Categories (id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(20)
            )
            """
TAGS_TABLE = """CREATE TABLE IF NOT EXISTS Tags (id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(20)
            )
            """
ARTICLES_TABLE = """CREATE TABLE IF NOT EXISTS Articles (id INT AUTO_INCREMENT PRIMARY KEY,
            title varchar(25),
            publication_date DATETIME,
            url TEXT,
            category_id INT,
            summary_id INT UNIQUE,
            FOREIGN KEY(category_id) REFERENCES Categories(id),
            FOREIGN KEY(summary_id) REFERENCES Summaries(id)
            )
            """
TAGS_ARTICLES_RELATIONSHIP_TABLE = """CREATE TABLE IF NOT EXISTS Tags_in_articles (
            article_id INT,
            tag_id INT,
            FOREIGN KEY(article_id) REFERENCES Articles(id),
            FOREIGN KEY(tag_id) REFERENCES Tags(id)
            )
            """
AUTHORS_ARTICLES_RELATIONSHIP_TABLE = """CREATE TABLE IF NOT EXISTS Authors_in_articles (
            article_id INT,
            author_id INT,
            FOREIGN KEY(article_id) REFERENCES Articles(id),
            FOREIGN KEY(author_id) REFERENCES Authors(id)
            )
            """


def initialize_database(user, password, host, database):
    with pymysql.connect(host=host, user=user, password=password,
                         cursorclass=pymysql.cursors.DictCursor) as connection_instance:
        with connection_instance.cursor() as cursor_instance:
            create_database = 'CREATE DATABASE IF NOT EXISTS ' + database
            use_database = 'USE ' + database
            cursor_instance.execute(create_database)
            cursor_instance.execute(use_database)
            cursor_instance.execute(AUTHORS_TABLE)
            cursor_instance.execute(SUMMARIES_TABLE)
            cursor_instance.execute(CATEGORIES_TABLE)
            cursor_instance.execute(TAGS_TABLE)
            cursor_instance.execute(ARTICLES_TABLE)
            cursor_instance.execute(TAGS_ARTICLES_RELATIONSHIP_TABLE)
            cursor_instance.execute(AUTHORS_ARTICLES_RELATIONSHIP_TABLE)


def show_and_describe_tables(user, password, host, database):
    with pymysql.connect(host=host, user=user, password=password, database=database,
                         cursorclass=pymysql.cursors.DictCursor) as connection_instance:
        with connection_instance.cursor() as cursor:
            cursor.execute('SHOW TABLES')
            results = cursor.fetchall()
            results = map(lambda x: x['Tables_in_' + DATABASE], results)
            for r in results:
                print(r, ':')
                cursor.execute('DESCRIBE ' + r)
                print(pd.DataFrame(cursor.fetchall()), '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='username of mysql', default=USER)
    parser.add_argument('-p', '--password', help='password of mysql', required=True)
    parser.add_argument('-host', help='url of database server', default=HOST)
    parser.add_argument('-db', '--database', help='Name of database to create', default=DATABASE)
    parser.add_argument('-print', help='Show the created DB and its tables', action='store_true')
    args = parser.parse_args()
    try:
        initialize_database(args.username, args.password, args.host, args.database)

        if args.print:
            show_and_describe_tables(args.username, args.password, args.host, args.database)
    except pymysql.err.Error as err:
        print(err.args)
        exit(1)


if __name__ == '__main__':
    main()
