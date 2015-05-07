import sqlite3
import lib
import db_client


def print_label_count(cursor, table_name):
    label_column = lib.story_label
    print_count(cursor, table_name, label_column, lib.SUCCESS)
    print_count(cursor, table_name, label_column, lib.NOT_SUCCESS)


# print count for a specific value
def print_count(cursor, table_name, column_name, column_value):
    print "{0} {1}: {2}".format(column_name, column_value, db_client.count(cursor, table_name, column_name, column_value))


def main():
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    print_label_count(cursor, table_name)



if __name__ == '__main__':
    main()
