import numpy as np
import lib
from sklearn.learning_curve import learning_curve
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB
from sklearn.cross_validation import train_test_split
import matplotlib.pyplot as plt
from sklearn import cross_validation


# plot confusion matrix
def plot_confusion_matrix(y_pred, y):
    plt.imshow(metrics.confusion_matrix(y, y_pred), cmap=plt.cm.binary, interpolation='nearest')
    plt.colorbar()
    plt.xlabel('true value')
    plt.ylabel('predicted value')


# plot learning curve
def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None, n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5)):
    """
        Generate a simple plot of the test and traning learning curve.
        Parameters
        ----------
        estimator : object type that implements the "fit" and "predict" methods
            An object of that type which is cloned for each validation.
        title : string
            Title for the chart.
        X : array-like, shape (n_samples, n_features)
            Training vector, where n_samples is the number of samples and
            n_features is the number of features.
        y : array-like, shape (n_samples) or (n_samples, n_features), optional
            Target relative to X for classification or regression;
            None for unsupervised learning.
        ylim : tuple, shape (ymin, ymax), optional
            Defines minimum and maximum yvalues plotted.
        cv : integer, cross-validation generator, optional
            If an integer is passed, it is the number of folds (defaults to 3).
            Specific cross-validation objects can be passed, see
            sklearn.cross_validation module for the list of possible objects
        n_jobs : integer, optional
            Number of jobs to run in parallel (default 1).
    """
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training Set Size")
    plt.ylabel("Error")

    train_sizes, train_scores, test_scores = learning_curve(estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_errors_mean = 1 - train_scores_mean
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_errors_mean = 1 - test_scores_mean
    test_scores_std = np.std(test_scores, axis=1)

    plt.grid()
    plt.fill_between(train_sizes, train_errors_mean - train_scores_std,
                     train_errors_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_errors_mean - test_scores_std,
                     test_errors_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_errors_mean, 'o-', color="r", label="Training Error")
    plt.plot(train_sizes, test_errors_mean, 'o-', color="g", label="Cross-Validation Error")
    plt.legend(loc="best")
    return plt


# experiment with sklearn decision tree and naive bayesian
def train_test(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    print '\ntraining data shape: {0}\ntesting data shape: {1}'.format(X_train.shape, X_test.shape)

    # fit a CART model to the data
    dTree = DecisionTreeClassifier()
    dTree.fit(X_train, y_train)
    y_pred = dTree.predict(X_test)

    print '\ndecision tree:'
    print "classification accuracy: {0}\n".format(metrics.accuracy_score(y_test, y_pred))
    plot_confusion_matrix(y_test, y_pred)
    #plt.show()

    # make predictions
    expected = y
    predicted = dTree.predict(X)

    # summarize the fit of the model
    print(metrics.classification_report(expected, predicted))
    print(metrics.confusion_matrix(expected, predicted))

    print '\nnaive bayesian:'
    gnb = GaussianNB()
    y_pred = gnb.fit(X, y).predict(X)
    print("number of mislabeled points out of a total {0} points : {1}".format(len(y), (y != y_pred).sum()))


def draw_learning_curve(file_name, title):
    f = open(file_name)
    feature_names = f.readline()  # skip the header
    num_columns = len(feature_names.split(','))
    data = np.loadtxt(fname=f, delimiter=',')
    print 'data shape: {0}'.format(data.shape)

    X = data[:, 0:num_columns-1]
    y = data[:, num_columns-1]
    # Cross validation with 100 iterations to get smoother mean test and train
    # score curves, each time with 20% data randomly selected as a validation set.
    cv = cross_validation.ShuffleSplit(len(y), n_iter=10, test_size=0.2, random_state=0)
    plot_learning_curve(DecisionTreeClassifier(), title, X, y, ylim=(-0.01, 0.5), cv=cv, n_jobs=4)


def main():
    print 'learning curve of oversampling and undersampling'
    draw_learning_curve(lib.OVER_SKLEARN_FILE,  'Oversampling Data')
    draw_learning_curve(lib.UNDER_SKLEARN_FILE,  'undersampling Data')

    print '\nlearning curve of oversampling on different sets of attributes'
    draw_learning_curve('data/over_metadata_simple_analysis_sklearn.csv',  'oversampling with metadata and simple text analysis')
    draw_learning_curve('data/over_metadata_simple_analysis_user_sklearn.csv', 'oversampling with metadata, simple text analysis and user info')
    draw_learning_curve('data/over_metadata_simple_analysis_topic_sklearn.csv',  'oversampling with metadata, simple text analysis and topic modeling')

    print '\nlearning curve of undersampling on different sets of attributes'
    draw_learning_curve('data/under_metadata_simple_analysis_sklearn.csv',  'undersampling with metadata and simple text analysis')
    draw_learning_curve('data/under_metadata_simple_analysis_user_sklearn.csv', 'undersampling with metadata, simple text analysis and user info')
    draw_learning_curve('data/under_metadata_simple_analysis_topic_sklearn.csv', 'undersampling with metadata, simple text analysis and topic modeling')

    plt.show()
    #train_test(X, y)





if __name__ == '__main__':
    main()
