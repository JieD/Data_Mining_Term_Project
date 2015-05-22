import sqlite3
import sys
import db_client
import lib
import export
from pprint import pprint as pp2
import string
import numpy as np
import pandas as pd
import nltk
from nltk.stem.snowball import SnowballStemmer
import re
import os
import codecs
from sklearn import feature_extraction
from random import randint


# fetch topic & terms to dictionary
def read_topics():
    print '\nread topics and terms'
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


def assign_topics(cursor, table_name, id_column):
    print '\nassign topic frequencies'
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
        """max_count = 0
        max_topic = 'none'
        for topic in lib.topic_term_dict.keys():
            #topic_count[topic] /= (1.0 * len(lib.topic_term_dict[topic]))
            if topic_count[topic] > max_count:
                max_count = topic_count[topic]
                max_topic = topic
        db_client.update(cursor, table_name, id_column, name, 'topic', max_topic)"""


# oversampling and undersampling
def resampling():
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

    #read_topics()
    #assign_topics(cursor, table_name, id_column)

    export.write(conn, table_name, not_success_out_file, success_out_file, 'ups', 'num_comments', 'image_provided', 'reciprocate',
                 'exchange', 'text_length', 'money', 'time', 'job', 'student', 'family', 'craving', 'label')

    resampling()

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
