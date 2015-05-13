import nltk, random, re, string
from nltk.classify import apply_features
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


class TextAnalysis():
    def __init__(self):
        self.regex = re.compile('[%s]' % re.escape(string.punctuation))
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words("english"))

    def train(self):
        print "Querying DB"
        # read samples from DB
        success_request = self.db.get_N_results("\\:\\)",num_samples)
        fail_request = self.db.get_N_results("\\:\\(",num_samples)

        print "Query Returned"
        # read query results into memory
        success_request = [(t["text"].split(" "),'positive') for t in success_request]
        fail_request = [(t["text"].split(" "),'negative') for t in fail_request]

        labeled_tweets = success_request + fail_request

        random.shuffle(labeled_tweets)

        print "compiling all words list"
        # extract all unique words from the tweets
        # these will be used as features
        self.all_words = self.get_all_words(labeled_tweets)

        # remove stop words
        self.all_words = self.all_words.difference(self.stop_words)
        print "num words: %d"%len(self.all_words)

        test_size = int(len(labeled_tweets) * TEST_SET_PROPORTION)

        # apply_features is a lazy loader, so that features are
        # computed as necessary, instead of being loaded into memory
        # all at once
        train_set = apply_features(self.document_features,labeled_tweets[:len(labeled_tweets) - test_size])
        test_set = apply_features(self.document_features,labeled_tweets[len(labeled_tweets) - test_size:])


        print "training"
        self.classifier = nltk.NaiveBayesClassifier.train(train_set)

        #print accuracy on test set
        print "Accuracy on "
        print(nltk.classify.accuracy(self.classifier, test_set))