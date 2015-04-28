import sqlite3
import lib
import db_client
from pprint import pprint as pp2


def assign_label(cursor):
    cursor = db_client.select_all(cursor, lib.RAW_ROAP_TABLE_NAME, lib.story_primary_key, 'title', 'author')
    for row in cursor:
        id = row[0]
        title = row[1]
        author = row[2][1:]
        label = check_title(title)
        if label == 1:
            'got pizza'


# check the tag information in the title
# if thanks, then the author got a pizza
# if not request nor thanks, then we are not interested
def check_title(title):
    first_word = title.split()[0]  # is tag
    #pp2(first_word)
    if 'request' not in first_word.lower():
        if 'thanks' in first_word.lower():  # assign success label
            pp2(title)
            return 1  # get pizza
        else:
            return -1  # not interested
    else:
        return 0  # request


# parse the title to find giver
def find_giver(title):
    return ''


def main():
    conn = sqlite3.connect(lib.DB_NAME)
    source_name = lib.RAW_ROAP_TABLE_NAME
    cursor = conn.cursor()
    cursor = db_client.select_all(cursor, source_name, lib.story_primary_key, 'title', 'author')
    story = cursor.fetchone()
    pp2(story)
    #title = story[1]
    #check_title(title)
    #assign_label(cursor)
    conn.close()


if __name__ == '__main__':
    main()