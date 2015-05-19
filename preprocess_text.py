import sqlite3
import re
import sys
import time
from time import time
import codecs
import db_client
import lib
import export
from pprint import pprint as pp2
import nltk
from nltk.stem.snowball import SnowballStemmer
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.decomposition import NMF


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
        #value = unicode(value).encode("utf-8")  # avoid encoding error (Unicode & ASCII)
        line += str(value) + "\n"
    line += "\n"
    return line


# extract all text, success and not success
def extract_text(cursor, table_name):
    print '\nextract all success text'

    """cursor = db_client.select_all(cursor, table_name, lib.intermediate_story_primary_key, 'edit_remove_text')
    store_text(cursor, lib.total_name, lib.total_text)
    cursor = db_client.select_condition_no(cursor, table_name, lib.story_label, lib.NOT_SUCCESS,
                                           lib.intermediate_story_primary_key, 'edit_remove_text')
    store_text(cursor, lib.total_not_success_name, lib.total_not_success_text)
    print 'total number of text: {0}'.format(len(lib.total_text))
    print 'total number of not success text: {0}'.format(len(lib.total_not_success_text))"""

    cursor = db_client.select_condition_no(cursor, table_name, lib.story_label, lib.SUCCESS,
                                           lib.intermediate_story_primary_key, 'edit_remove_text')
    store_text(cursor, lib.total_success_name, lib.total_success_text)
    print 'total number of success text: {0}'.format(len(lib.total_success_text))


# store all text fetched from cursor to text_list
def store_text(cursor, name_list, text_list):
    all_rows = cursor.fetchall()
    for row in all_rows:
        name = row[0]
        text = row[1]
        name_list.append(name)
        text_list.append(text)


# extract image_provided and reciprocate
def simple_text_analysis(cursor, table_name, id_column):
    print '\ncheck image_provided and reciprocate'
    cursor = db_client.select_all(cursor, table_name, id_column, 'edit_remove_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1]
        is_image_provided = check_image_included(text)
        will_reciprocate = check_reciprocate(text)
        db_client.update(cursor, table_name, id_column, name, 'image_provided', is_image_provided)
        db_client.update(cursor, table_name, id_column, name, 'reciprocate', will_reciprocate)


# count the text length after removing stopwords and non-letters
def count_text_length(cursor, table_name, id_column):
    print '\ncheck text length after removing stopwords'
    cursor = db_client.select_all(cursor, table_name, id_column, 'edit_remove_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1].lower()

        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        stopwords_removed_tokens = [token for token in tokens if token not in lib.stopwords]  # remove stopwords

        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
        for token in stopwords_removed_tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)

        db_client.update(cursor, table_name, id_column, name, 'text_length', len(filtered_tokens))

    """lib.total_words.extend(filtered_tokens)
    stems = [lib.stemmer.stem(t) for t in filtered_tokens]
    lib.total_words_stemmed.extend(stems)
    print "total number of filtered tokens: {0}".format(len(lib.total_words))
    print "total number of unique filtered tokens: {0}".format(len(set(lib.total_words)))
    print text, '\n'
    print "number of tokens: {0}\nnumber of tokens after stopwords removed: {1}".format(len(tokens), len(filtered_tokens))
    print filtered_tokens, '\n', stems"""
    """print 'tokens: {0}\n'.format(lib.total_words[:500])
    print 'stemmed tokens: {0}\n'.format(lib.total_words_stemmed[:500])"""


# tokenize and stem the text
def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    noun_tokens = extract_nouns(filtered_tokens)
    stems = [lib.stemmer.stem(t) for t in noun_tokens]
    return stems


# only tokenize the text
def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return extract_nouns(filtered_tokens)


def extract_nouns(tokens):
    word_tag_paris = nltk.pos_tag(tokens)
    noun_tokens = [token for (token, tag) in word_tag_paris if tag == 'NN']
    return noun_tokens


# associates words with its stems (note repetition exists)
def create_word_stem_dictionary():
    print '\nbuild vocabulary frame:'

    for text in lib.total_success_text:
        tokenized_words = tokenize_only(text)
        lib.total_words.extend(tokenized_words)
        stemmed_words = [lib.stemmer.stem(t) for t in tokenized_words]
        lib.total_words_stemmed.extend(stemmed_words)


    lib.vocab_frame = pd.DataFrame({'words': lib.total_words}, index=lib.total_words_stemmed)
    print 'there are ' + str(lib.vocab_frame.shape[0]) + ' items in vocab_frame'
    #print lib.vocab_frame


# build tf_idf
def apply_tf_idf(text_list):
    print '\napply tf_idf'
    #define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.2, min_df = 0.1, stop_words='english', tokenizer=tokenize_and_stem)
    lib.tfidf_matrix = tfidf_vectorizer.fit_transform(text_list)  #fit the vectorizer to text_list
    print(lib.tfidf_matrix.shape)

    lib.terms = tfidf_vectorizer.get_feature_names()
    lib.dist = 1 - cosine_similarity(lib.tfidf_matrix)
    #print lib.terms
    #print lib.dist


def apply_kmeans():
    num_clusters = lib.number_topics
    km = KMeans(n_clusters=num_clusters)
    km.fit(lib.tfidf_matrix)
    joblib.dump(km, lib.cluster_doc)
    #km = joblib.load(lib.cluster_doc)
    clusters = km.labels_.tolist()

    requests = {'name': lib.total_success_name, 'text': lib.total_success_text, 'cluster': clusters}
    frame = pd.DataFrame(requests, index=[clusters], columns=['name', 'cluster'])
    print '\ncluster counts:\n', frame['cluster'].value_counts(), '\n'  # number of stories per cluster (clusters from 0 to 4)

    #grouped = frame['rank'].groupby(frame['cluster']) #groupby cluster for aggregation purposes
    #print grouped.mean() #average rank (1 to 100) per cluster

    print("Top terms per cluster:")
    #sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    #print order_centroids
    for i in range(num_clusters):
        print "\nCluster {0} words:".format(i)

        for index in order_centroids[i, :lib.number_topic_features]:  # replace 6 with n words per cluster
            print ' {0}'.format(lib.vocab_frame.ix[lib.terms[index].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore')),
        print '\n'

        """print "Cluster {0} names:".format(i)
        for name in frame.ix[i]['name'].values.tolist():
            print ' {0},'.format(name)
        print '\n'
        """
    print '\n'



def apply_nmf():
    # Fit the NMF model
    print '\nfit the NMF model'
    t0 = time()
    nmf = NMF(n_components=lib.number_topics, random_state=1).fit(lib.tfidf_matrix)
    print("done in %0.3fs." % (time() - t0))

    for topic_idx, topic in enumerate(nmf.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([lib.terms[i]
                        for i in topic.argsort()[:-lib.number_topic_features - 1:-1]]))
        print()


def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # init
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    #simple_text_analysis(cursor, table_name, id_column)
    #count_text_length(cursor, table_name, id_column)

    extract_text(cursor, table_name)
    create_word_stem_dictionary()
    apply_tf_idf(lib.total_success_text)
    apply_kmeans()
    apply_nmf()

    """print_request(cursor, table_name, lib.SUCCESS, lib.SUCCESS_FILE)
    print_request(cursor, table_name, lib.NOT_SUCCESS, lib.NOT_SUCCESS_FILE)
    #quick_query(cursor, table_name, 'author', 'CDearsVVV', 'selftext')
    export.write(conn, table_name, lib.OUT_FILE, 'ups', 'num_comments', 'edited', 'reciprocate', 'image_provided', 'text_length', 'label')"""

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
