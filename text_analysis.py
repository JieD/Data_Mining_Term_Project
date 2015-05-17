import sqlite3
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
#import mpld3


def clean_text(cursor, table_name, id_column):
    #cursor = db_client.select_all(cursor, table_name, id_column, 'selftext')
    cursor = db_client.select_condition_no(cursor, table_name, lib.story_label, lib.NOT_SUCCESS, id_column, 'selftext')
    #cursor = db_client.select_condition_no(cursor, table_name, id_column, 't3_2sgcak', id_column, 'selftext')
    all_rows = cursor.fetchall()
    for row in all_rows:
        name = row[0]
        text = row[1]
        text = unicode(text).encode("utf-8")  # avoid encoding error (Unicode & ASCII)
        stemmer = SnowballStemmer("english")

        text = extract_edit(name, text, stemmer)
        #print text
        #tokenize_and_stem(stemmer, text)


def extract_edit_sentences(cursor, table_name, id_column, label, file_name):
    out_file = open(file_name, 'w')
    out_file.write("Edit sentences for table = {0}, label = {1}\n\n".format(table_name, label))
    cursor = db_client.select_condition_no(cursor, table_name, lib.story_label, label, id_column, 'selftext')
    all_rows = cursor.fetchall()
    for row in all_rows:
        name = row[0]
        text = row[1]
        text = unicode(text).encode("utf-8")  # avoid encoding error (Unicode & ASCII)
        extract_edit(name, text, out_file)


# analyse sentences containing edit
# steps:
# 1. find all paragraphs
# 2. check whether contain edit (note only the sentences starting with edit)
# 3. if yes, tokenize the paragraphs
# 4. look for following words to identify request label:
#    'thank to',
# if identifying label from edit, remove the paragraph containing edit
def extract_edit(name, text, out_file):
    final_text = []
    edit = re.compile(r'\b(edit)\b', re.I)
    edit_start = False

    if edit.search(text) is not None:  # contain edit
        #print name
        out_file.write("{0}\n".format(name))
        paragraphs = text.split('\n')
        for paragraph in paragraphs:  # extract the paragraph containing edit, but only start with sentences containing edit
            if edit.search(paragraph):  # paragraph contains edit
                edit_sents = []
                for sent in lib.sent_detector.tokenize(paragraph.strip(), realign_boundaries=True):
                    if edit_start or edit.search(sent) is not None:
                        edit_start = True
                        edit_sents.append(sent)  # only interested in sentences came after edit
                        #print sent
                        out_file.write(sent + '\n')
                    else:
                        final_text.append("{0} ".format(sent))  # sentence not contains edit
            else:
                final_text.append("{0}\n".format(paragraph))  # paragraph not contains edit
        #print
        out_file.write("\n")
    return final_text


#
def check_got_pizza(sents):
    text = ' '.join(sents)
    received = re.compile(r'\b(pizza received|thanks|thank|fulfilled|delivered|offer)\b', re.I)
    for sent in sents:
        if re.search(received, sent) is not None and 'n\'t' not in sent:
            print sent
            print 'got pizza'
            break
        else:
            return False


# tokenize and stem the text
def tokenize_and_stem(stemmer, text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems


# tokenize the text
def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens


def main():
    # init
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    extract_edit_sentences(cursor, table_name, id_column, lib.NOT_SUCCESS, lib.EDIT_NOT_SUCCESS_FILE)
    extract_edit_sentences(cursor, table_name, id_column, lib.SUCCESS, lib.EDIT_SUCCESS_FILE)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
