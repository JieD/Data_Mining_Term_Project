from pprint import pprint
import json
import sys
import sqlite3
import lib
import reddit_client
import db_client


# add user info columns to raw roap table
def update_raw_table(cursor, table_name):
    db_client.add_columns(cursor, table_name, lib.USER_INFO_DICT)


# get user info from reddit, save to db
def extract_user_info(cursor, table_name, id_column, client):
    cursor = db_client.select_all(cursor, table_name, id_column, 'author')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        author = row[1]

        data = get_about_user(client, author)
        if 'error' in data:
            db_client.delete(cursor, table_name, id_column, name)
            print name
        else:
            data = data['data']
            db_client.update(cursor, table_name, id_column, name, 'comment_karma', data['comment_karma'])
            db_client.update(cursor, table_name, id_column, name, 'link_karma', data['link_karma'])
            db_client.update(cursor, table_name, id_column, name, 'account_created_utc', data['created_utc'])


# get 'about user'
def get_about_user(client, author):
    #parameters = {'sort': 'new', 'limit': 100, 'restrict_sr': 'on', 'syntax': 'cloudsearch'}
    url = r'http://www.reddit.com/user/{un}/about/.json'.format(un=author)
    #url = r'http://www.reddit.com/search.json?q=subreddit:Random_Acts_Of_Pizza+author:the'
    r = client.get(url)
    #print 'sent URL is', r.url
    j = json.loads(r.text)
    #pprint(j)
    #data = j['data']
    #comments = j['data']['children']
    #num_comment = len(comments)
    #print "user has {0} comments".format(num_comment)
    #print data['comment_karma'], "\n", data['link_karma'], '\n', data['created_utc']
    return j


def is_user_name(name):
    client = reddit_client.login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)
    url = r'http://www.reddit.com/search.json?q=subreddit:Random_Acts_Of_Pizza+author:{0}'.format(name)
    r = client.get(url)
    print 'sent URL is', r.url
    j = json.loads(r.text)


# calculate account age when requesting
def calculate_account_age(cursor, table_name, id_column):
    db_client.add_column(cursor, table_name, 'account_age', lib.FLOAT_TYPE)
    cursor = db_client.select_all(cursor, table_name, id_column, 'account_created_utc', 'created_utc')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        account_created = row[1]
        request_created = row[2]
        account_age = request_created - account_created
        db_client.update(cursor, table_name, id_column, name, 'account_age', account_age)


def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # init
    conn = sqlite3.connect(lib.DB_NAME)
    #table_name = lib.RAW_ROAP_TABLE_NAME
    table_name = lib.FULL_RAW_ROAP_TABLE_NAME
    id_column = lib.raw_story_primary_key
    cursor = conn.cursor()

    client = reddit_client.login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)
    update_raw_table(cursor, table_name)
    extract_user_info(cursor, table_name, id_column, client)
    calculate_account_age(cursor, table_name, id_column)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
