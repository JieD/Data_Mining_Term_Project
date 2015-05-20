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


# fetch topic & terms to dictionary
def read_topics():
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


def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # init
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    read_topics()
    assign_topics(cursor, table_name, id_column)

    export.write(conn, table_name, lib.OUT_FILE, 'ups', 'num_comments', 'image_provided', 'reciprocate',
                 'exchange', 'text_length', 'money', 'job', 'student', 'family', 'craving', 'label')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
