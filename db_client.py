import sqlite3
import csv
import pandas.io.sql as sql
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


def create_story_table(cursor, table_name, primary_key, primary_key_type, field_dict):
    # creating a table with 1 column and set it as PRIMARY KEY
    create_table_with_primary_key(cursor, table_name, primary_key, primary_key_type)
    # add the rest columns
    add_columns(cursor, table_name, field_dict)


# add columns according to dictionary
def add_columns(cursor, table_name, field_dict):
    for key in field_dict.keys():
        value = field_dict[key]
        add_column(cursor, table_name, key, value)

# insert a new row, but only id is provided
def insert_id(cursor, table_name, id_column, id_value):
    cursor.execute("INSERT OR IGNORE INTO {tn} ({idc}) VALUES (?)".format(tn=table_name, idc=id_column), (id_value,))


# update one column of the row
def update(cursor, table_name, id_column, id_value, column_name, column_value):
    cursor.execute("UPDATE {tn} SET {cn}=(?) WHERE {idc}=(?)".
                   format(tn=table_name, cn=column_name, idc=id_column), (column_value, id_value))


# delete the row
def delete(cursor, table_name, column_name, column_value):
    cursor.execute("DELETE FROM {tn} WHERE {cn} = (?) ".format(tn=table_name, cn=column_name), (column_value,))


# retrieve data from specified columns, no need to order
def select_all(cursor, table_name, *args):
    columns = combine_columns(*args)
    cursor.execute("SELECT {cns} FROM {tn}".format(cns=columns, tn=table_name))
    return cursor


# retrieve data meet certain criteria without order
def select_condition_no(cursor, table_name, column_name, column_value, *args):
    columns = combine_columns(*args)
    cursor.execute("SELECT {cns} FROM {tn} WHERE {cn}=?".
                   format(cns=columns, tn=table_name, cn=column_name), (column_value,))
    return cursor


# retrieve data meet certain criteria with order
def select_condition(cursor, table_name, column_name, column_value, order_column, *args):
    columns = combine_columns(*args)
    cursor.execute("SELECT {cns} FROM {tn} WHERE {cn}=? ORDER BY {oc} ASC".
                   format(cns=columns, tn=table_name, cn=column_name, oc=order_column), (column_value,))
    return cursor


# form the sql query for columns
def combine_columns(*args):
    columns = args[0]
    for arg in args[1:]:
        columns += ', ' + arg
    return columns


# form the sql query for column list
def parse_column_list(column_list):
    columns = column_list[0]
    for arg in column_list[1:]:
        columns += ', ' + arg
    return columns


def cpy_columns(cursor, source, destination, source_column_list, destination_column_list, condition_column, condition_column_value):
    source_columns = parse_column_list(source_column_list)
    destination_columns = parse_column_list(destination_column_list)
    cursor.execute("INSERT INTO {dtn} ({dcs}) SELECT {scs} FROM {stn} WHERE {cn} = (?)".
                   format(dtn=destination, dcs=destination_column_list, scs=source_column_list, stn=source,
                          cn=condition_column), (condition_column_value,))


"""
# export table to csv file (not working due to encoding error) - use export.py
def export(cursor, table_name, csv_file_name, column_list):
    columns = parse_column_list(column_list)
    data = cursor.execute("SELECT {cns} FROM {tn}".format(cns=columns, tn=table_name))

    with open(csv_file_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)


# use pandas to export sql table to csv - error, not able to recognize the table (wrong db name)
def export1(conn, table_name, csv_file_name, column_list):
    columns = parse_column_list(column_list)
    conn = sqlite3.connect(database.db)
    table = sql.read_frame("SELECT * FROM {tn}".format(cns=columns, tn=table_name), conn)
    table.to_csv(csv_file_name)
"""


# count the number of records meet specific criteria
def count(cursor, table_name, column_name, column_value):
    cursor = cursor.execute("SELECT COUNT({cn}) FROM {tn} WHERE {cn}=(?)".format(cn=column_name, tn=table_name),
                            (column_value,))
    row = cursor.fetchone()
    return row[0]


# get distince values
def get_distinct_values(cursor, table_name, column_name):
    cursor = cursor.execute("SELECT DISTINCT {cn} FROM {tn}".format(cn=column_name, tn=table_name))
    rows = cursor.fetchall()  # each row is a tuple
    values = []
    for row in rows:
        values.append(row[0])  # only one element in the tuple
    return values


# insert one row
def insert_story(cursor, table_name, story):
    idc = lib.raw_story_primary_key
    idv = story[idc]
    insert_id(cursor, table_name, idc, idv)

    for key in lib.RAW_FIELDS_DICT.keys():
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
    print "start query reddit"
    after_name = ''
    limit = lib.QUERY_LIMIT

    while True:
        json_stories = reddit_client.query_stories_in_time_range(client, start_time, end_time, sr=sr, limit=limit,
                                                                 after=after_name)
        stories = reddit_client.parse_stories(json_stories)

        if not stories:  # empty list (probably has fetched 1000 stories for the request
            end_time = last_story['created_utc']
            if start_time < end_time:
                # adjust timestamp throw in delta (Day_Seconds) to overcome the bias in the reddit search result
                end_time += lib.DAY_SECONDS
                continue
            else:
                break
        # store stories into the db
        insert_stories(cursor, table_name, stories)
        length = len(stories)
        lib.count += length
        last_story = stories[length - 1]
        after_name = last_story['name']

    print "finish query reddit\n"


def main():
    # connecting to the database file
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.RAW_ROAP_TABLE_NAME
    cursor = conn.cursor()

    #delete_table(cursor, table_name)
    #create_story_table(cursor, table_name, lib.raw_story_primary_key, lib.raw_story_primary_key_type, lib.RAW_FIELDS_DICT)
    client = reddit_client.login(lib.USERNAME, lib.PASSWORD, lib.USER_AGENT)

    # retrieve the latest 1000 stories
    #get_stories_in_year(client, lib.ROAP, lib.START_2015, cursor, lib.RAW_ROAP_TABLE_NAME, lib.FILE_NAME)

    # retrieve stories in the given time period
    end_time = time.time()
    get_stories_in_time_range(client, lib.ROAP, lib.START_2015, end_time, cursor, lib.RAW_ROAP_TABLE_NAME, lib.FILE_NAME)

    # committing changes and closing the connection to the database file
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()