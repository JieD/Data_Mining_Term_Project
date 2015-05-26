import sqlite3
import sys
import time
import db_client
import lib
import export
from pprint import pprint as pp2
import string
import nltk
from random import randint


# fetch topic & terms to dictionary
def read_topics():
    print 'read topics and terms'
    in_file = open(lib.topic_doc, 'r')
    while 1:
        line = in_file.readline()
        if line == '':  # EOF
            in_file.close()
            break
        topic_terms = line.split(':')
        topic = topic_terms[0]
        terms = topic_terms[1].split()
        lib.topic_term_dict[topic] = [lib.stemmer.stem(term) for term in terms]
        #print topic
        #print lib.topic_term_dict[topic]


# count the frequency of words for each request belonging to each topic
def topic_terms_frequency(cursor, table_name, id_column):
    print '\nassign topic counts'
    cursor = db_client.select_all(cursor, table_name, id_column, 'tokenized_text')
    all_rows = cursor.fetchall()
    for row in all_rows:
        name = row[0]
        text = row[1]

        topic_count = {}
        for topic in lib.topic_term_dict.keys():
            topic_count[topic] = 0

        words = [word for word in nltk.word_tokenize(text)]
        stemmed_words = [lib.stemmer.stem(word) for word in words]
        for word in stemmed_words:
            for topic in lib.topic_term_dict.keys():
                if word in lib.topic_term_dict[topic]:
                    topic_count[topic] += 1
                    break

        for topic in lib.topic_term_dict.keys():
            db_client.update(cursor, table_name, id_column, name, topic, topic_count[topic])
        """ not assigning one topic, but multiple topics to a request
        max_count = 0
        max_topic = 'none'
        for topic in lib.topic_term_dict.keys():
            #topic_count[topic] /= (1.0 * len(lib.topic_term_dict[topic]))
            if topic_count[topic] > max_count:
                max_count = topic_count[topic]
                max_topic = topic
        db_client.update(cursor, table_name, id_column, name, 'topic', max_topic)"""


# oversampling and undersampling
def resampling(cursor, table_name):
    print '\ncreate dataset using oversampling and undersampling'
    label_column = lib.story_label
    lib.success_count = db_client.count(cursor, table_name, label_column, lib.SUCCESS)
    lib.not_success_count = db_client.count(cursor, table_name, label_column, lib.NOT_SUCCESS)
    count_dif = lib.not_success_count - lib.success_count
    success_list = read_file_to_list(lib.SUCCESS_OUT_FILE)
    not_success_list = read_file_to_list(lib.NOT_SUCCESS_OUT_FILE)

    success_index = []
    not_success_index = []
    for i in range(0, count_dif):
        success_index.append(randint(0, lib.success_count - 1))
    for j in range(0, lib.success_count):
        not_success_index.append(randint(0, lib.not_success_count - 1))

    write_file(success_list, success_index, not_success_list, lib.OVER_FILE)
    write_file(not_success_list, not_success_index, success_list, lib.UNDER_FILE)

    out_file = open(lib.OVER_FILE, 'a')
    for line in success_list:
        out_file.write(line)
    out_file.close()


# read the file by line and save to list
def read_file_to_list(file_name):
    in_file = open(file_name, 'r')
    lib.file_header = in_file.readline()  # skip header
    save_list = []
    while 1:
        line = in_file.readline()
        if line == '':  # EOF
            in_file.close()
            break
        save_list.append(line)
    return save_list


# write selected items from lists to out_file
def write_file(source_list, index_list, add_list, out_file_name):
    out_file = open(out_file_name, 'w')
    out_file.write(lib.file_header)
    for i in range(0, len(index_list)):
        index = index_list[i]
        out_file.write(source_list[index])
    for i in range(0, len(add_list)):
        out_file.write(add_list[i])
    out_file.close()



def count_yearly(cursor, table_name):
    create_column = 'created'
    success_count_2011 = db_client.count_yearly_success(cursor, table_name, create_column, lib.START_2011, lib.START_2012)
    success_count_2012 = db_client.count_yearly_success(cursor, table_name, create_column, lib.START_2012, lib.START_2013)
    success_count_2013 = db_client.count_yearly_success(cursor, table_name, create_column, lib.START_2013, lib.START_2014)
    success_count_2014 = db_client.count_yearly_success(cursor, table_name, create_column, lib.START_2014, lib.START_2015)
    success_count_2015 = db_client.count_yearly_success(cursor, table_name, create_column, lib.START_2015, time.time())

    count_2011 = db_client.count_yearly(cursor, table_name, create_column, lib.START_2011, lib.START_2012)
    count_2012 = db_client.count_yearly(cursor, table_name, create_column, lib.START_2012, lib.START_2013)
    count_2013 = db_client.count_yearly(cursor, table_name, create_column, lib.START_2013, lib.START_2014)
    count_2014 = db_client.count_yearly(cursor, table_name, create_column, lib.START_2014, lib.START_2015)
    count_2015 = db_client.count_yearly(cursor, table_name, create_column, lib.START_2015, time.time())
    print '\nreport yearly count:\n 2011: {0} - {1}\n 2012: {2} - {3}\n 2013: {4} - {5}\n 2014: {6} - {7}\n 2015: {8} - {9}'.\
        format(success_count_2011, count_2011, success_count_2012, count_2012, success_count_2013, count_2013,
               success_count_2014, count_2014, success_count_2015, count_2015)


def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # init
    conn = sqlite3.connect(lib.DB_NAME)
    """table_name = lib.ROAP_TABLE_NAME
    out_file = lib.OUT_FILE"""
    table_name = lib.FULL_ROAP_TABLE_NAME
    out_file = lib.FULL_OUT_FILE
    success_out_file = lib.SUCCESS_OUT_FILE
    not_success_out_file = lib.NOT_SUCCESS_OUT_FILE
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    read_topics()
    topic_terms_frequency(cursor, table_name, id_column)
    count_yearly(cursor, table_name)

    export.write(conn, table_name, out_file, not_success_out_file, success_out_file, 'account_age', 'account_created_utc',
                 'link_karma', 'comment_karma', 'ups', 'num_comments', 'image_provided', 'reciprocate', 'exchange',
                 'text_length', 'money', 'time', 'job', 'student', 'family', 'craving', 'label')
    resampling(cursor, table_name)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
