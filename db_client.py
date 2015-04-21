import sqlite3
import lib
import reddit_client


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


def insert(cursor, table_name, id_column, id_value, column_name, column_value):
    cursor.execute("UPDATE {tn} SET {cn}=(?) WHERE {idc}=(?)".
                   format(tn=table_name, cn=column_name, idc=id_column), (column_value, id_value))


def create_story_table(cursor, table_name):
    # creating a table with 1 column and set it as PRIMARY KEY
    create_table_with_primary_key(cursor, table_name, lib.story_primary_key, lib.story_primary_key_type)

    # add columns
    for key in lib.STORY_FIELDS_DICT.keys():
        value = lib.STORY_FIELDS_DICT[key]
        add_column(cursor, table_name, key, value)


def insert_id(cursor, table_name, id_column, id_value):
    cursor.execute("INSERT INTO {tn} ({idc}) VALUES (?)".format(tn=table_name, idc=id_column), (id_value,))


def insert_story(cursor, table_name, story):
    idc = lib.story_primary_key
    idv = story[idc]
    insert_id(cursor, table_name, idc, idv)

    for key in lib.STORY_FIELDS_DICT.keys():
        cv = story[key]
        insert(cursor, table_name, idc, idv, key, cv)


def insert_stories(cursor, table_name, stories):
    for story in stories:
        insert_story(cursor, table_name, story)


def get_stories_in_range(start_time):



def main():
    # connecting to the database file
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.RAW_ROAP_TABLE_NAME
    cursor = conn.cursor()

    delete_table(cursor, table_name)
    create_story_table(cursor, table_name)
    stories = reddit_client.main()
    insert_stories(cursor, table_name, stories)

    # committing changes and closing the connection to the database file
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()