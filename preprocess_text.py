import sqlite3
import re
import sys
import db_client
import lib
import export
from pprint import pprint as pp2
import nltk
from nltk.stem.snowball import SnowballStemmer


# return the number of words in a string
def get_text_length(s):
    words = s.split()
    return len(words)


# check include image
def check_image_included(text):
    image_feature = re.compile(r'(imgur\.|\.jpg|\.png|\.tif|\.gif)', re.I)
    return image_feature.search(text) is not None


# check whether is willing to reciprocate
def check_reciprocate(text):
    reciprocate_feature = re.compile(r'(pay it forward|pay it back|return the favor)', re.I)
    return reciprocate_feature.search(text) is not None


# print requests (belong to specified label) to file
def print_request(cursor, table_name, label, file_name):
    cursor = db_client.select_condition(cursor, table_name, 'label', label, 'created_utc',
                                        lib.intermediate_story_primary_key, 'author', 'edited', 'image_provided',
                                        'reciprocate', 'text_length', 'title', 'edit_remove_text')
    all_rows = cursor.fetchall()
    out_file = open(file_name, 'w')

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


# extract image_provided and reciprocate
def simple_text_analysis(cursor, table_name, id_column):
    cursor = db_client.select_all(cursor, table_name, id_column, 'edit_remove_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1]
        #text_length = get_text_length(text)
        is_image_provided = check_image_included(text)
        will_reciprocate = check_reciprocate(text)
        #db_client.update(cursor, table_name, id_column, name, 'text_length', text_length)
        db_client.update(cursor, table_name, id_column, name, 'image_provided', is_image_provided)
        db_client.update(cursor, table_name, id_column, name, 'reciprocate', will_reciprocate)


# tokenize and stem, save to the global lists
def tokenize_all(cursor, table_name, id_column):
    cursor = db_client.select_all(cursor, table_name, id_column, 'edit_remove_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1]

        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        stopwords_removed_tokens = [token for token in tokens if token not in lib.stopwords]  # remove stopwords

        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
        for token in stopwords_removed_tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)

        db_client.update(cursor, table_name, id_column, name, 'text_length', len(filtered_tokens))
        lib.total_words.extend(filtered_tokens)
        stems = [lib.stemmer.stem(t) for t in filtered_tokens]
        lib.total_words_stemmed.extend(stems)

    print 'tokens: {0}\n'.format(lib.total_words)
    print 'stemmed tokens: {0}\n'.format(lib.total_words_stemmed)


def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # init
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    simple_text_analysis(cursor, table_name, id_column)
    tokenize_all(cursor, table_name, id_column)

    print_request(cursor, table_name, lib.SUCCESS, lib.SUCCESS_FILE)
    print_request(cursor, table_name, lib.NOT_SUCCESS, lib.NOT_SUCCESS_FILE)

    #quick_query(cursor, table_name, 'author', 'CDearsVVV', 'selftext')

    export.write(conn, table_name, lib.OUT_FILE, 'ups', 'num_comments', 'edited', 'reciprocate', 'image_provided', 'text_length', 'label')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
