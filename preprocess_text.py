import sqlite3
import re
import sys
import time
from time import time
import db_client
import lib
import export
from pprint import pprint as pp2
import nltk
from nltk.stem.snowball import SnowballStemmer
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
    reciprocate_feature = re.compile(r'(pay it forward|pay it back|return the favor|repay)', re.I)
    return reciprocate_feature.search(text) is not None


def check_exchange(text):
    exchange_feature = re.compile(r'(trade|in return)', re.I)
    return exchange_feature.search(text) is not None


# extract image_provided and reciprocate
def simple_text_analysis(cursor, table_name, id_column):
    print '\ncheck image_provided, reciprocate and exchange'
    cursor = db_client.select_all(cursor, table_name, id_column, 'edit_remove_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1]
        is_image_provided = check_image_included(text)
        will_reciprocate = check_reciprocate(text)
        will_exchange = check_exchange(text)
        db_client.update(cursor, table_name, id_column, name, 'image_provided', is_image_provided)
        db_client.update(cursor, table_name, id_column, name, 'reciprocate', will_reciprocate)
        db_client.update(cursor, table_name, id_column, name, 'exchange', will_exchange)


# count the text length after removing non-letters
# store text in tokenized_text
def tokenize_and_count_length(cursor, table_name, id_column):
    print '\ncheck text length and tokenize'
    cursor = db_client.select_all(cursor, table_name, id_column, 'edit_remove_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1].lower()
        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        #stopwords_removed_tokens = [token for token in tokens if token not in lib.stopwords]  # remove stopwords

        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        tokenized_text = ' '.join(filtered_tokens)
        db_client.update(cursor, table_name, id_column, name, 'text_length', len(filtered_tokens))
        db_client.update(cursor, table_name, id_column, name, 'tokenized_text', tokenized_text)


# remove nltk and application specific stopwords, http links - only for success text
def remove_stopwords_and_non_nouns(cursor, table_name, id_column):
    print '\nremove stopwords and non-nouns:'
    t0 = time()

    cursor = db_client.select_condition_no(cursor, table_name, lib.story_label, lib.SUCCESS, id_column, 'tokenized_text')
    all_rows = cursor.fetchall()

    for row in all_rows:
        name = row[0]
        text = row[1].lower()
        #print text, '\n'

        tokens = [token for token in nltk.word_tokenize(text)]
        stopwords_removed_tokens = [token for token in tokens if token not in lib.stopwords and token not in lib.custom_stopwords]  # remove stopwords
        #print ' '.join(stopwords_removed_tokens), '\n'

        filtered_tokens = []
        for token in stopwords_removed_tokens:
            if 'http' not in token:  # remove http link
                filtered_tokens.append(token)

        noun_tokens = extract_nouns(filtered_tokens)
        noun_text = ' '.join(noun_tokens)
        noun_stemmed_tokens = [lib.stemmer.stem(token) for token in noun_tokens]
        noun_stemmed_text = ' '.join(noun_stemmed_tokens)
        db_client.update(cursor, table_name, id_column, name, 'tokenized_text', noun_text)
        db_client.update(cursor, table_name, id_column, name, 'tokenized_stemmed_text', noun_stemmed_text)
        #print noun_text, '\n'
    print("done in %0.3fs." % (time() - t0))


# use POS-tagging to find nouns
def extract_nouns(tokens):
    word_tag_paris = nltk.pos_tag(tokens)
    #print word_tag_paris, '\n'
    noun_tokens = [token for (token, tag) in word_tag_paris if 'NN' in tag]
    return noun_tokens


# extract all success text and store in lists
def extract_text_for_analysis(cursor, table_name):
    print '\nextract all success text and tokens'
    cursor = db_client.select_condition_no(cursor, table_name, lib.story_label, lib.SUCCESS,
                                           lib.intermediate_story_primary_key, 'tokenized_text')
    store_text_and_tokens(cursor, lib.total_success_name, lib.total_success_text, lib.total_success_words,
                          lib.total_stemmed_success_words)
    print 'total number of success text: {0}'.format(len(lib.total_success_text))

    """cursor = db_client.select_all(cursor, table_name, lib.intermediate_story_primary_key, 'edit_remove_text')
    store_text(cursor, lib.total_name, lib.total_text)
    cursor = db_client.select_condition_no(cursor, table_name, lib.story_label, lib.NOT_SUCCESS,
                                           lib.intermediate_story_primary_key, 'edit_remove_text')
    store_text(cursor, lib.total_not_success_name, lib.total_not_success_text)
    print 'total number of text: {0}'.format(len(lib.total_text))
    print 'total number of not success text: {0}'.format(len(lib.total_not_success_text))"""


# store all text fetched from cursor to lists for further analysis
def store_text_and_tokens(cursor, name_list, text_list, token_list, stemmed_token_list):
    all_rows = cursor.fetchall()
    for row in all_rows:
        name = row[0]
        text = row[1]
        name_list.append(name)
        text_list.append(text)
        tokens = nltk.word_tokenize(text)
        stemmed_tokens = [lib.stemmer.stem(t) for t in tokens]
        token_list.extend(tokens)
        stemmed_token_list.extend(stemmed_tokens)
        #text_list.append(' '.join(stemmed_tokens))


# associates words with its stems (note repetition exists)
def create_word_stem_dictionary():
    print '\nbuild vocabulary frame:'
    t0 = time()
    lib.vocab_frame = pd.DataFrame({'words': lib.total_success_words}, index=lib.total_stemmed_success_words)
    print("done in %0.3fs." % (time() - t0))
    print 'there are ' + str(lib.vocab_frame.shape[0]) + ' items in vocab_frame'
    #print lib.vocab_frame


# tokenize and stem the text
def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [lib.stemmer.stem(t) for t in filtered_tokens]
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
    return filtered_tokens


# build tf_idf
def apply_tf_idf(text_list):
    print '\napply tf_idf'
    t0 = time()
    # define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.3, min_df=0.01, stop_words='english', tokenizer=tokenize_and_stem)
    lib.tfidf_matrix = tfidf_vectorizer.fit_transform(text_list)  # fit the vectorizer to text_list
    print("done in %0.3fs." % (time() - t0))
    print(lib.tfidf_matrix.shape)

    lib.terms = tfidf_vectorizer.get_feature_names()
    lib.dist = 1 - cosine_similarity(lib.tfidf_matrix)
    #print lib.terms
    #print lib.dist


# use kmeans to find clusters and top terms
def apply_kmeans():
    print '\napply kmeans:'
    t0 = time()
    out_file = open(lib.kmeans_topics_doc, 'w')
    num_clusters = lib.number_topics
    km = KMeans(n_clusters=num_clusters)
    km.fit(lib.tfidf_matrix)
    joblib.dump(km, lib.cluster_doc)
    #km = joblib.load(lib.cluster_doc)
    clusters = km.labels_.tolist()
    print("done in %0.3fs." % (time() - t0))

    requests = {'name': lib.total_success_name, 'text': lib.total_success_text, 'cluster': clusters}
    frame = pd.DataFrame(requests, index=[clusters], columns=['name', 'cluster'])
    print '\ncluster counts:\n', frame['cluster'].value_counts(), '\n'  # number of stories per cluster
    out_file.write('\ncluster counts:\n{0}\n\n'.format(frame['cluster'].value_counts()))

    #grouped = frame['rank'].groupby(frame['cluster']) #groupby cluster for aggregation purposes
    #print grouped.mean() #average rank (1 to 100) per cluster

    print("Top terms per cluster:")
    #sort cluster centers by proximity to centroid
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    #print order_centroids
    for i in range(num_clusters):
        print "\nCluster {0} words:".format(i)
        out_file.write('Cluster {0} words:\n'.format(i))

        for index in order_centroids[i, :lib.number_topic_features]:  # n words per cluster
            term = lib.vocab_frame.ix[lib.terms[index].split(' ')].values.tolist()[0][0]
            print ' {0}'.format(term),
            out_file.write('{0} '.format(term))
        print '\n'
        out_file.write('\n\n')

        """print "Cluster {0} names:".format(i)
        for name in frame.ix[i]['name'].values.tolist():
            print ' {0},'.format(name)
        print '\n'
        """
    out_file.close()


# use nmf for topic modeling
def apply_nmf():
    # Fit the NMF model
    print '\nfit the NMF model'
    t0 = time()
    nmf = NMF(n_components=lib.number_topics, random_state=1).fit(lib.tfidf_matrix)
    print("done in %0.3fs." % (time() - t0))

    out_file = open(lib.nmf_topics_doc, 'w')
    for topic_idx, topic in enumerate(nmf.components_):
        print("Topic #%d:" % topic_idx)
        out_file.write('Topic #{}:\n'.format(topic_idx))
        terms = " ".join([lib.terms[i] for i in topic.argsort()[:-lib.number_topic_features - 1:-1]])
        out_file.write('{}\n\n'.format(terms))
        print terms
        print
    out_file.close()


# print requests (belong to specified label) to file
def print_request(cursor, table_name, label, file_name):
    cursor = db_client.select_condition(cursor, table_name, 'label', label, 'created_utc',
                                        lib.intermediate_story_primary_key, 'author', 'edited', 'image_provided',
                                        'reciprocate', 'exchange', 'text_length', 'title', 'edit_remove_text')
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



def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # init
    conn = sqlite3.connect(lib.DB_NAME)
    table_name = lib.ROAP_TABLE_NAME
    #table_name = lib.FULL_ROAP_TABLE_NAME
    id_column = lib.intermediate_story_primary_key
    cursor = conn.cursor()

    simple_text_analysis(cursor, table_name, id_column)
    tokenize_and_count_length(cursor, table_name, id_column)
    remove_stopwords_and_non_nouns(cursor, table_name, id_column)

    extract_text_for_analysis(cursor, table_name)
    create_word_stem_dictionary()
    apply_tf_idf(lib.total_success_text)
    apply_kmeans()
    apply_nmf()

    """print_request(cursor, table_name, lib.SUCCESS, lib.SUCCESS_FILE)
    print_request(cursor, table_name, lib.NOT_SUCCESS, lib.NOT_SUCCESS_FILE)
    #quick_query(cursor, table_name, 'author', 'CDearsVVV', 'selftext')
    export.write(conn, table_name, lib.OUT_FILE, 'ups', 'num_comments', 'image_provided', 'reciprocate',
                 'exchange', 'text_length', 'label')"""

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
