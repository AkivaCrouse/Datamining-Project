import pymysql
import argparse
import pandas as pd
from config import *
# pd.set_option('display.max_rows', None)


def initialize_database(user, password, host, database):
    """
    create the database with all the tables
    :param user: username of mysql
    :param password: password of mysql
    :param host: url of database server
    :param database: database to save to
    """
    with pymysql.connect(host=host, user=user, password=password,
                         cursorclass=pymysql.cursors.DictCursor) as connection_instance:
        with connection_instance.cursor() as cursor_instance:
            create_database = 'CREATE DATABASE IF NOT EXISTS ' + database
            use_database = 'USE ' + database
            cursor_instance.execute(create_database)
            cursor_instance.execute(use_database)
            cursor_instance.execute(AUTHORS_CREATION)
            cursor_instance.execute(SUMMARIES_CREATION)
            cursor_instance.execute(CATEGORIES_CREATION)
            cursor_instance.execute(TAGS_CREATION)
            cursor_instance.execute(ARTICLES_CREATION)
            cursor_instance.execute(TAGS_ARTICLES_RELATIONSHIP_CREATION)
            cursor_instance.execute(AUTHORS_ARTICLES_RELATIONSHIP_CREATION)
            cursor_instance.execute(CATEGORIES_ARTICLES_RELATIONSHIP_CREATION)


def show_and_describe_tables(user, password, host, database):
    """
    present the database data
    :param user: username of mysql
    :param password: password of mysql
    :param host: url of database server
    :param database: database to save to
    :return:
    """
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
                cursor.execute(f'SELECT * FROM {r}')
                print(pd.DataFrame(cursor.fetchall()), '\n')


def drop_database(user, password, host, database):
    """
    delete the whole database
    :param user: username of mysql
    :param password: password of mysql
    :param host: url of database server
    :param database: database to save to
    :return:
    """
    with pymysql.connect(host=host, user=user, password=password,
                         cursorclass=pymysql.cursors.DictCursor) as connection_instance:
        with connection_instance.cursor() as cursor:
            cursor.execute(f'DROP DATABASE {database}')


def reset_database(user, password, host, database):
    """
    reset the database to have 0 rows in each table
    :param user: username of mysql
    :param password: password of mysql
    :param host: url of database server
    :param database: database to save to
    :return:
    """
    drop_database(user, password, host, database)
    initialize_database(user, password, host, database)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='username of mysql', default=USER)
    parser.add_argument('-p', '--password', help='password of mysql', required=True)
    parser.add_argument('-host', help='url of database server', default=HOST)
    parser.add_argument('-db', '--database', help='Name of database to create', default=DATABASE)
    parser.add_argument('--print', help='Show the created DB and its tables', action='store_true')
    parser.add_argument('--delete', help='Clean database for tests', action='store_true')
    parser.add_argument('--reset', help='Reset database for tests', action='store_true')
    args = parser.parse_args()
    try:
        initialize_database(args.username, args.password, args.host, args.database)
        if args.reset:
            reset_database(args.username, args.password, args.host, args.database)
        if args.print:
            show_and_describe_tables(args.username, args.password, args.host, args.database)
        if args.delete:
            drop_database(args.username, args.password, args.host, args.database)
    except pymysql.err.Error as err:
        print(err.args)
        exit(1)


if __name__ == '__main__':
    main()
