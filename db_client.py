import sqlite3
import lib
import reddit_client
import time
from pprint import pprint as pp2


# create a new table from db
def create_table(cursor, table_name):
    cursor.execute('CREATE TABLE {tn}'.format(tn=table_name))


# create a new table with primary key setup
# note that PRIMARY KEY column must consist of unique values!
def create_table_with_primary_key(cursor, table_name, primary_field, primary_field_type):
    cursor.execute('CREATE TABLE {tn} ({pf} {pft} PRIMARY KEY)'
                   .format(tn=table_name, pf=primary_field, pft=primary_field_type))


# delete table from db
def delete_table(cursor, table_name):
    cursor.execute('DROP TABLE {tn}'.format(tn=table_name))


def add_column(cursor, table_name, column_name, column_type):
    cursor.execute("ALTER TABLE {tn} ADD COLUMN {cn} {ct}"
                   .format(tn=table_name, cn=column_name, ct=column_type))


def add_column_with_default(cursor, table_name, column_name, column_type, default_value):
    cursor.execute("ALTER TABLE {tn} ADD COLUMN {cn} {ct} DEFAULT {df}"
                   .format(tn=table_name, cn=column_name, ct=column_type, df=default_value))


def create_story_table(cursor, table_name):
    # creating a table with 1 column and set it as PRIMARY KEY
    create_table_with_primary_key(cursor, table_name, lib.story_primary_key, lib.story_primary_key_type)

    # add the rest columns
    for key in lib.STORY_FIELDS_DICT.keys():
        value = lib.STORY_FIELDS_DICT[key]
        add_column(cursor, table_name, key, value)


# insert a new row, but only id is provided
def insert_id(cursor, table_name, id_column, id_value):
    cursor.execute("INSERT OR IGNORE INTO {tn} ({idc}) VALUES (?)".format(tn=table_name, idc=id_column), (id_value,))


# update one column of the row
def update(cursor, table_name, id_column, id_value, column_name, column_value):
    cursor.execute("UPDATE {tn} SET {cn}=(?) WHERE {idc}=(?)".
                   format(tn=table_name, cn=column_name, idc=id_column), (column_value, id_value))


# insert one row
def insert_story(cursor, table_name, story):
    idc = lib.story_primary_key
    idv = story[idc]
    insert_id(cursor, table_name, idc, idv)

    for key in lib.STORY_FIELDS_DICT.keys():
        cv = story[key]
        update(cursor, table_name, idc, idv, key, cv)


# insert multiple stories
def insert_stories(cursor, table_name, stories):
    for story in stories:
        insert_story(cursor, table_name, story)


def get_stories_in_year(client, sr, start_time, cursor, table_name, file_name):
    out_f = open(file_name, 'w')
    out_f.write("Start recording fetch info for {0}\n".format(sr))
    first_story = reddit_client.first_query(client, lib.ROAP)
    insert_story(cursor, table_name, first_story)

    after_name = first_story['name']
    while True:
        json_stories = reddit_client.query_stories(client, sr=sr, after=after_name)
        stories = reddit_client.parse_stories(json_stories)
        length = len(stories)
        if length == 0:
            break
        last_story = stories[length - 1]
        after_name = last_story['name']
        insert_stories(cursor, table_name, stories)
        lib.count += lib.QUERY_LIMIT

        if lib.count % lib.THRESHOLD == 0:
            out_f.write("The {0}th story: name = {1}, author = {2}\n".
                        format(str(lib.count), last_story['name'], last_story['author']))

        if stories[length - 1]['created'] <= start_time:
            print "break the while loop"
            break

    out_f.write("Finish recording fetch into for {0}\n".format(sr))
    out_f.close()


# use search with timestamp (regular query can only fetch the latest 1000 stories)
def get_stories_in_time_range(client, sr, start_time, end_time, cursor, table_name, file_name):
    out_f = open(file_name, 'w')
    out_f.write("Start recording fetch info for {0}\n".format(sr))
    after_name = ''
    limit = lib.QUERY_LIMIT

    while start_time + lib.DAY_SECONDS < end_time:
        while 1:
            json_stories = reddit_client.query_stories_in_time_range(client, start_time, end_time, limit=limit,
                                                                     after=after_name)
            stories = reddit_client.parse_stories(json_stories)
            if stories:  # not empty list
                insert_stories(cursor, table_name, stories)
            else:  # empty list (probably has fetched 1000 stories for the request
                break

            length = len(stories)
            lib.count += length
            last_story = stories[length - 1]
            after_name = last_story['name']
            if length is not limit:
                break
            if lib.count % lib.THRESHOLD == 0:
                out_f.write("The {0}th story: name = {1}, author = {2}\n".
                            format(str(lib.count), last_story['name'], last_story['author']))

        # adjust timestamp, throw in delta (Day_Seconds) to overcome the bias in the reddit search result
        end_time = last_story['created_utc'] + lib.DAY_SECONDS

    out_f.write("Finish recording fetch into for {0}\n".format(sr))
    out_f.close()


def main():
    # connecting to the database file
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.RAW_ROAP_TABLE_NAME
    cursor = conn.cursor()

    delete_table(cursor, table_name)
    create_story_table(cursor, table_name)

    client = reddit_client.login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)
    #get_stories_in_year(client, lib.ROAP, lib.START_2014, cursor, lib.RAW_ROAP_TABLE_NAME, lib.FILE_NAME)
    end_time = time.time()
    get_stories_in_time_range(client, lib.ROAP, lib.START_2014, end_time, cursor, lib.RAW_ROAP_TABLE_NAME, lib.FILE_NAME)

    # committing changes and closing the connection to the database file
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()