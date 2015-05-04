import sqlite3
import lib
import db_client
from pprint import pprint as pp2


# find the matching thanks to request (got pizza)
def assign_label(cursor, source, destination):
    source_id_column = lib.raw_story_primary_key
    destination_id_column = lib.intermediate_story_primary_key
    cursor = db_client.select_all(cursor, source, source_id_column, 'created', 'title', 'author', 'created', 'created_utc')
    all_rows = cursor.fetchall()

    i = 0
    for row in all_rows:
        name = row[0]
        title = row[1]
        label = check_title(title)
        author = row[2][1:]
        created = row[3]
        created_utc = row[4]

        # insert request & thanks into destination
        if label is not lib.OTHERS:
            i += 1
            db_client.insert_id(cursor, destination, destination_id_column, name)
            db_client.update(cursor, destination, destination_id_column, name, lib.story_label, label)
            db_client.update(cursor, destination, destination_id_column, name, 'requester_username', author)
            db_client.update(cursor, destination, destination_id_column, name, 'request_title', title)
            db_client.update(cursor, destination, destination_id_column, name, 'unix_timestamp_local_of_request', created)
            db_client.update(cursor, destination, destination_id_column, name, 'unix_timestamp_utc_of_request', created_utc)
    print "Retrieve {0} requests & thanks".format(i)


# check the tag information in the title
# if thanks, then the author got a pizza
# if not request nor thanks, then we are not interested
def check_title(title):
    first_word = title.split()[0]  # tag
    #pp2(first_word)
    if 'request' not in first_word.lower():
        if 'thanks' in first_word.lower():
            #pp2(title)
            return lib.THANKS  # got pizza
        else:
            return lib.OTHERS  # not interested
    else:
        return lib.REQUEST  # request


# parse the title to find giver
def find_giver(title):
    return ''


# find matching thanks & requests
# find all thanks
# for each thanks:
#   find all the posts (before the post time) made by the author
#   the closest one is the request that is fulfilled
def match_thank_request(cursor):
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    order_column = 'unix_timestamp_utc_of_request'

    # get all thanks
    cursor = db_client.select_condition(cursor, table_name, id_column, lib.story_label, lib.THANKS, order_column)
    all_rows = cursor.fetchall()

    for row in all_rows:
        pp2(row[0])



def create_intermediate_table(cursor, table_name):
    db_client.create_story_table(cursor, table_name, lib.intermediate_story_primary_key,
                                 lib.intermediate_story_primary_key_type, lib.INTERMEDIATE_FIELDS_DICT)


def main():
    # init
    conn = sqlite3.connect(lib.DB_NAME)
    source_name = lib.RAW_ROAP_TABLE_NAME
    table_name = lib.ROAP_TABLE_NAME
    cursor = conn.cursor()
    db_client.delete_table(cursor, table_name)
    create_intermediate_table(cursor, table_name)

    #
    #cursor = db_client.select_all(cursor, source_name, lib.raw_story_primary_key, 'title', 'author')
    #story = cursor.fetchone()
    #pp2(story)
    #title = story[1]
    #check_title(title)

    assign_label(cursor, source_name, table_name)
    match_thank_request(cursor)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()