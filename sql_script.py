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
            cursor_instance.execute(CREATE_DATABASE + database)
            sql_logger.info("Created database if doesn't exist already.")
            cursor_instance.execute(USE_DATABASE + database)
            cursor_instance.execute(AUTHORS_CREATION)
            sql_logger.info("Created Authors table if doesn't exist already.")
            cursor_instance.execute(SUMMARIES_CREATION)
            sql_logger.info("Created Summaries table if doesn't exist already.")
            cursor_instance.execute(CATEGORIES_CREATION)
            sql_logger.info("Created Categories table if doesn't exist already.")
            cursor_instance.execute(TAGS_CREATION)
            sql_logger.info("Created Tags table if doesn't exist already.")
            cursor_instance.execute(ARTICLES_CREATION)
            sql_logger.info("Created Articles table if doesn't exist already.")
            cursor_instance.execute(TAGS_ARTICLES_RELATIONSHIP_CREATION)
            sql_logger.info("Created tags-articles Relationship table if doesn't exist already.")
            cursor_instance.execute(AUTHORS_ARTICLES_RELATIONSHIP_CREATION)
            sql_logger.info("Created author-articles Relationship table if doesn't exist already.")
            cursor_instance.execute(CATEGORIES_ARTICLES_RELATIONSHIP_CREATION)
            sql_logger.info("Created categories-articles Relationship table if doesn't exist already.")


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
            results = map(lambda x: x['Tables_in_' + database], results)
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
    sql_logger.info(f'Deleted the database {database}.')


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
    sql_logger.info(f'Reset the database {database}.')


def select_top_ten_tags(user, password, host, database):
    """
    Retrieves the ten most popular tags and returns a dataframe.
    :param user: username of mysql
    :param password: password of mysql
    :param host: url of database server
    :param database: database to save to
    :return: dataframe of 10 most popular tags and their respective tag counts.
    """
    with pymysql.connect(host=host, user=user, password=password, database=database,
                         cursorclass=pymysql.cursors.DictCursor) as connection_instance:
        with connection_instance.cursor() as cursor:
            cursor.execute(TOP_TEN_TAGS)
            results = cursor.fetchall()
            return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='username of mysql', default=USER)
    required = parser.add_argument_group('required arguments')
    required.add_argument('-p', '--password', help='password of mysql', required=True)
    parser.add_argument('-host', help='url of database server', default=HOST)
    parser.add_argument('-db', '--database', help='Name of database to create', default=DATABASE)
    parser.add_argument('--print', help='Show the created DB and its tables', action='store_true')
    parser.add_argument('--delete', help='Clean database for tests', action='store_true')
    parser.add_argument('--reset', help='Reset database for tests', action='store_true')
    # parser.add_argument('--top10', help='Prints the 10 most common tags', action='store_true')
    args = parser.parse_args()
    try:
        initialize_database(args.username, args.password, args.host, args.database)
        if args.reset:
            reset_database(args.username, args.password, args.host, args.database)
        if args.print:
            show_and_describe_tables(args.username, args.password, args.host, args.database)
        if args.delete:
            drop_database(args.username, args.password, args.host, args.database)
        # if args.top10:
        #     print(select_top_ten_tags(args.username, args.password, args.host, args.database))
    except pymysql.err.Error as err:
        sql_logger.error(err.args)
        print(err.args)
        exit(1)


if __name__ == '__main__':
    main()
