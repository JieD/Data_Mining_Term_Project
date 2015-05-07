import sqlite3
import db_client
import lib
import export
from pprint import pprint as pp2


# return the number of words in a string
def get_text_length(s):
    words = s.split()
    return len(words)


# check if the string include a hyperlink
def include_link(s):
    return lib.HYPERLINK_FEATURE in s


# print text for success
def print_success(cursor):
    cursor = db_client.select_condition(cursor, lib.ROAP_TABLE_NAME, 'label', lib.SUCCESS, 'created_utc',
                                        lib.intermediate_story_primary_key, 'author', 'text_length', 'link_provided',
                                        'selftext')
    all_rows = cursor.fetchall()
    out_file = open(lib.SUCCESS_FILE, 'w')

    for row in all_rows:
        out_file.write(form_output(row))
    out_file.close()


# print query result for verification
def quick_query(cursor, table_name, column_name, column_value, *args):
    cursor = db_client.select_condition(cursor, table_name, column_name, column_value, 'created_utc', *args)
    all_rows = cursor.fetchall()

    for row in all_rows:
        pp2(form_output(row))
        print


# form string of query result for print
def form_output(row):
    line = ""
    for value in row:
        value = unicode(value).encode("utf-8")  # avoid encoding error (Unicode & ASCII)
        line += str(value) + "\n"
    line += "\n"
    return line



def simple_text_analysis(cursor, table_name, id_column):
    cursor = db_client.select_all(cursor, table_name, id_column, 'selftext')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1]
        text_length = get_text_length(text)
        link_provided = include_link(text)
        db_client.update(cursor, table_name, id_column, name, 'text_length', text_length)
        db_client.update(cursor, table_name, id_column, name, 'link_provided', link_provided)


def main():
    # init
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    simple_text_analysis(cursor, table_name, id_column)
    print_success(cursor)
    quick_query(cursor, table_name, 'author', 'CDearsVVV', 'selftext')

    export.write(conn, table_name, lib.OUT_FILE, 'ups', 'num_comments', 'edited', 'text_length', 'link_provided', 'label')


    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
