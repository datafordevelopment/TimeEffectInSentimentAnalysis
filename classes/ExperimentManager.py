from config import *
from random import randint

import numpy as np

from scipy import *
from scipy import sparse

from matplotlib import pyplot as plt

from sklearn.svm import SVC
from sklearn.metrics import *
from sklearn.utils import shuffle
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer


class ExperimentManager:
    """
    This class consists core methods of an active learning experiment.
    """
    def __init__(self, experiment_number, years_tweets_counts, n=1, analyzer='word'):
        """
        Constructor method
        :param experiment_number: int
        :param years_tweets_counts: dict
        :param n: int
        :param analyzer: string
        :return: ExperimentManager
        """

        self.__n = n
        self.__all_scores = {}
        self.__feature_count = 0
        self.__analyzer = analyzer
        self.__experiment_number = experiment_number
        self.__years_tweets_counts= years_tweets_counts

        self.__label_encoder = preprocessing.LabelEncoder()
        self.__label_encoder.fit(SENTIMENT_CLASSES)

    def run_experiment(self, document, classes):
        """
        Main method for using resources and making method calls in order.
        :param document: list
        :param classes: list
        :return: dict
        """
        # Fitting document
        X_sparse, features = self._fit_document(document)

        self.__feature_count = len(features)
        self.__features = features

        # Getting in ndarray format
        X = X_sparse.toarray()

        # Splitting document for years
        years_X, years_X_sparse, years_y = self._split_dataset_to_years(X, X_sparse, classes)

        # Shuffling them for the experiment
        years_X, years_X_sparse, years_y = self._shuffle_years(years_X, years_X_sparse, years_y)

        # Creating 500, 300, 200 and 50 chunks of data
        partitioned_X_sparse, partitioned_y = self._create_years_partitions(years_X_sparse, years_y)

        # Iterating over lines' setups dict
        self._go_over_lines_setups(partitioned_X_sparse, partitioned_y)
        """
        Example self.__all_scores by now:
        {
            'line4': {
                '2013_200+2012_500/2013_300': 0.61,
                '2014_200+2012_500/2014_300': 0.53,
                '2015_200+2012_500/2015_300': 0.51
            },
            'line2': {
                '2013_50+2012_500/2013_300': [0.59, 0.59, 0.6, 0.57, 0.6, 0.57, 0.59, 0.58, 0.6, 0.6],
                '2015_50+2012_500/2015_300': [0.51, 0.52, 0.49, 0.5, 0.49, 0.5, 0.51, 0.5, 0.52, 0.5],
                '2014_50+2012_500/2014_300': [0.51, 0.52, 0.52, 0.5, 0.5, 0.5, 0.51, 0.52, 0.51, 0.51]
            },
            'line1': {
                '2012_500/2014_300': 0.51,
                '2012_500/2015_300': 0.5,
                '2012_500/2013_300': 0.59
            }
        }
        """


        # Now let's cumulate line2's scores
        self._cumulate_scores_of_line2()
        """
        Example self.__all_scores by now:
        self.__all_scores = {
            'line4': {
                '2013_200+2012_500/2013_300': 0.60999999999999999,
                '2014_200+2012_500/2014_300': 0.51000000000000001,
                '2015_200+2012_500/2015_300': 0.53000000000000003
            },
            'line3': {
                'L1-2012_500+2015_50/2015_300': 0.5033333333333333,
                'L1-2012_500+2014_50/2014_300': 0.5,
                'L1-2012_500+2013_50/2013_300': 0.58666666666666667,

                'L2-2012_500+2015_50/2015_300': 0.5033333333333333,
                'L2-2012_500+2014_50/2014_300': 0.5,
                'L2-2012_500+2013_50/2013_300': 0.58666666666666667,

                'L3-2012_500+2015_50/2015_300': 0.5033333333333333,
                'L3-2012_500+2014_50/2014_300': 0.5,
                'L3-2012_500+2013_50/2013_300': 0.58666666666666667

            },
            'line2': {
                '2013_50+2012_500/2013_300': [0.56333333333333335, 0.58833333333333326, 0.60999999999999999],
                '2015_50+2012_500/2015_300': [0.49666666666666665, 0.51533333333333342, 0.53000000000000003],
                '2014_50+2012_500/2014_300': [0.48333333333333334, 0.49133333333333329, 0.5]
            },
            'line1': {
                '2012_500/2014_300': 0.46333333333333332,
                '2012_500/2015_300': 0.52000000000000002,
                '2012_500/2013_300': 0.58333333333333337
            }
        }
        """
        return self.__all_scores

    def _fit_document(self, document):
        """
        Fits document and generates n-grams and features
        :param document: list
        :return: csr_matrix, list
        """
        vectorizer = CountVectorizer(ngram_range=(self.__n, self.__n), analyzer=self.__analyzer)
        X = vectorizer.fit_transform(document)
        features = vectorizer.get_feature_names()
        return X, features

    def _split_dataset_to_years(self, X, X_sparse, y):
        """
        Splits dataset to each year respectively
        :param X: dense data
        :param X_sparse: scipy.sparse
        :param y: list
        :return: dense matrice, scipy.sparse, list
        """

        start_index = 0
        years_X = {}
        years_y = {}
        years_X_sparse = {}

        for year, tweet_count in self.__years_tweets_counts.iteritems():
            end_index = start_index + tweet_count
            years_X[year] = X[start_index:end_index]
            years_y[year] = y[start_index:end_index]
            years_X_sparse[year] = X_sparse[start_index:end_index]
            start_index += tweet_count

        return years_X, years_X_sparse, years_y

    def _shuffle_years(self, years_X, years_X_sparse, years_y):
        """
        Shuffles years' tweets
        :param years_X: dense data
        :param years_X_sparse: scipy.sparse
        :param years_y: list
        :return: dense matrice, scipy.sparse, list
        """
        for year_name, year_data in years_X_sparse.iteritems():
            normal = years_X[year_name]
            sparse = years_X_sparse[year_name]
            labels = years_y[year_name]
            years_X[year_name], years_X_sparse[year_name], years_y[year_name] = shuffle(normal, sparse, labels)

        return years_X, years_X_sparse, years_y

    def _create_years_partitions(self, years_X, years_y):
        """
        Creates partitions of each year
        :param years_X: scipy.sparse
        :param years_y: list
        :return: scipy.sparse, list
        """
        splitted_X = {}
        splitted_y = {}

        for (year_X, year_X_data), (year_y, year_y_data) in zip(years_X.iteritems(), years_y.iteritems()):

            splitted_X[year_X] = {}
            splitted_y[year_y] = {}

            if not year_X in TEST_YEARS and not year_y in TEST_YEARS:
                splitted_X[year_X]['500'] = year_X_data
                splitted_y[year_y]['500'] = year_y_data

            else:
                start_index = 0
                end_index = year_X_data.shape[0]

                splitted_X[year_X]['300'] = year_X_data[start_index:start_index+300]
                splitted_X[year_X]['200'] = year_X_data[start_index+300:end_index]
                splitted_X[year_X]['50']  = []

                splitted_y[year_y]['300'] = year_y_data[start_index:start_index+300]
                splitted_y[year_y]['200'] = year_y_data[start_index+300:end_index]
                splitted_y[year_y]['50']  = []

        for test_year in TEST_YEARS:

            for j in range(0,LINE2_RANDOM_ITERATION_NUMBER):
                random_X_set = []
                random_y_set = []

                test_year_200_length = splitted_X[test_year]['200'].shape[0]
                random.seed()
                random_start_index = randint(0, test_year_200_length-RANDOM_SAMPLE_SIZE)
                random_end_index = random_start_index+RANDOM_SAMPLE_SIZE

                random_X_set = splitted_X[test_year]['200'][random_start_index:random_end_index]
                random_y_set = splitted_y[test_year]['200'][random_start_index:random_end_index]

                splitted_X[test_year]['50'].append(random_X_set)
                splitted_y[test_year]['50'].append(random_y_set)

        return splitted_X, splitted_y

    def _go_over_lines_setups(self, years_X_sparse, years_y):
        """
        Iterates over LINES_SETUPS dictionary to run classifications
        :param years_X_sparse: scipy.sparse
        :param years_y: list
        :return: void
        """

        # Iterating over lines
        for line_name, line_value in LINES_SETUPS.iteritems():
            print('Currently running on Experiment #'+str(self.__experiment_number)+', '+line_name)
            self.__all_scores[line_name] = {}

            # Iterating over each setup( say 500-2012, 200-2013 / 300-2013)
            for iteration_index, (train_set_setup, test_set_setup) in enumerate(zip(line_value['train'],
                                                                                    line_value['test'])):

                if line_name == "line1" or line_name == "line4":

                    X_train, X_test, y_train, y_test, train_set_name, test_set_name = \
                            self._create_train_and_test_sets_from_setup_dict(years_X_sparse, years_y, train_set_setup, test_set_setup, line_name, -1)

                    acc_score = self._classify(X_train, X_test, y_train, y_test)
                    self._save_accuracy_score(line_name, train_set_name, test_set_name, acc_score)

                elif line_name == "line2":

                    for random_50_iteration_index in range(0, LINE2_RANDOM_ITERATION_NUMBER):

                        X_train, X_test, y_train, y_test, train_set_name, test_set_name = \
                        self._create_train_and_test_sets_from_setup_dict(years_X_sparse, years_y, train_set_setup,
                                                                         test_set_setup, line_name, random_50_iteration_index)

                        acc_score = self._classify(X_train, X_test, y_train, y_test)
                        self._save_accuracy_score(line_name, train_set_name, test_set_name, acc_score)

                elif line_name == "line3":

                    # Find train set and test set - preperation
                    probability_setup = LINE3_PROB_SETUP[iteration_index]
                    prob_train_setup = probability_setup['train']
                    prob_test_setup = probability_setup['test']

                    prob_train_year, prob_train_count = prob_train_setup[0], prob_train_setup[1]
                    prob_test_year, prob_test_count = prob_test_setup[0], prob_test_setup[1]

                    prob_X_train = years_X_sparse[prob_train_year][prob_train_count]
                    prob_y_train = years_y[prob_train_year][prob_train_count]

                    prob_X_test = years_X_sparse[prob_test_year][prob_test_count]
                    prob_y_test = np.array(years_y[prob_test_year][prob_test_count])

                    final_X_test_year = test_set_setup.keys()[0] #2013
                    final_X_test_tweet_count = test_set_setup[final_X_test_year] #300

                    final_X_test = years_X_sparse[final_X_test_year][final_X_test_tweet_count]
                    final_y_test = years_y[final_X_test_year][final_X_test_tweet_count]

                    test_set_name = final_X_test_year + "_" + final_X_test_tweet_count
                    train_set_name_appendix = prob_train_year + "_" + prob_train_count + "+" + prob_test_year + "_" + str(MOST_DISTINCT_SAMPLE_SIZE)


                    # Active Learning Method - I
                    samples_closest_to_decision_boundary_X, samples_closest_to_decision_boundary_y = \
                        self._choose_ale_samples_closest_to_decision_boundary(prob_X_train, prob_X_test, prob_y_train, prob_y_test)

                    acc_score_for_ale_one = self._combine_train_sets_and_run_classification(prob_X_train, final_X_test,
                                                                                            samples_closest_to_decision_boundary_X,
                                                                                            prob_y_train, final_y_test,
                                                                                            samples_closest_to_decision_boundary_y)

                    train_set_name = "L1-" + train_set_name_appendix
                    self._save_accuracy_score(line_name, train_set_name, test_set_name, acc_score_for_ale_one)


                    # Active Learning Method - II
                    #train_set_name = "L2-" + train_set_name_appendix
                    #self._save_accuracy_score(line_name, train_set_name, test_set_name, acc_score)


                    # Active Learning Method - III
                    #train_set_name = "L3-" + train_set_name_appendix
                    #self._save_accuracy_score(line_name, train_set_name, test_set_name, acc_score)



    def _create_train_and_test_sets_from_setup_dict(self, years_X_sparse, years_y, train_setup, test_setup, line_name, iteration_number):
        """
        Creates necessary train set and test set from given setup dictionary
        :param years_X_sparse: scipy.sparse
        :param years_y: list
        :param train_setup: dict
        :param test_setup: dict
        :param line_name: string
        :param iteration_number: int
        :return: scipy.sparse, scipy.sparse, list, list, string, string
        """

        X_train = []
        y_train = []

        X_test  = []
        y_test  = []

        train_set_name = ""
        test_set_name = ""

        # Train setup and test setup may have different number of elements so we can't zip() and iterate simultaniously

        for train_set_year, tweet_to_take_from_train_year in train_setup.iteritems():

            new_x_train = years_X_sparse[train_set_year][tweet_to_take_from_train_year]

            if line_name == "line2" and isinstance(new_x_train, list) and len(new_x_train)==LINE2_RANDOM_ITERATION_NUMBER:
                new_x_train = new_x_train[iteration_number]

            new_x_train_dense = new_x_train.toarray().tolist()
            X_train += new_x_train_dense

            new_y_train = years_y[train_set_year][tweet_to_take_from_train_year]

            if line_name == "line2" and isinstance(y_train, list) and len(new_y_train)==LINE2_RANDOM_ITERATION_NUMBER:
                y_train += new_y_train[iteration_number]
            else:
                y_train += new_y_train

            train_set_name += train_set_year + '_' + tweet_to_take_from_train_year + '+'

        X_train_sparse = sparse.csr_matrix(X_train)
        train_set_name = train_set_name.rstrip('+')

        for test_set_year, tweet_to_take_from_test_year in test_setup.iteritems():

            new_x_test = years_X_sparse[test_set_year][tweet_to_take_from_test_year]
            new_x_test_dense = new_x_test.toarray().tolist()
            X_test += new_x_test_dense

            y_test += years_y[test_set_year][tweet_to_take_from_test_year]

            test_set_name += test_set_year + '_' + tweet_to_take_from_test_year + '+'

        sparse_X_test = sparse.csr_matrix(X_test)
        test_set_name = test_set_name.rstrip('+')

        return X_train_sparse, sparse_X_test, y_train, y_test, train_set_name, test_set_name

    def _classify(self, X_train, X_test, y_train, y_test):
        """
        Makes a classification with given train and test sets
        :param X_train: scipy.sparse
        :param X_test: scipy.sparse
        :param y_train: list
        :param y_test: list
        :return: float
        """
        # Creating SVM instance
        classifier = self._get_new_model_for_general_purpose()

        y_train = self.__label_encoder.transform(y_train)
        y_test  = self.__label_encoder.transform(y_test)

        # Fitting model
        classifier.fit(X_train, y_train)

        # Predicting
        predictions = classifier.predict(X_test)

        # Getting accuracy score
        acc_score = accuracy_score(y_test, predictions)
        #acc_score = round(acc_score, 3)

        return acc_score

    def _save_accuracy_score(self, line_name, train_set_name, test_set_name, score):
        """
        Saves given accuracy score to appropriate key
        :param line_name: string
        :param point_name: string
        :param score: float
        :return: void
        """
        score_dict_key = train_set_name + '/' + test_set_name

        if line_name == "line2":
            if not score_dict_key in self.__all_scores[line_name]:
                self.__all_scores[line_name][score_dict_key] = []
            self.__all_scores[line_name][score_dict_key].append(score)
        else:
            self.__all_scores[line_name][score_dict_key] = score

    def _cumulate_scores_of_line2(self):
        """
        Cumulates line2's scores from LINE2_RANDOM_ITERATION_NUMBER experiments into an array like: [min, mean, max]
        :return: void
        """
        # Iterating over line2's scores
        for train_test_set, scores_list in self.__all_scores['line2'].iteritems():

            min_ = np.min(scores_list)
            mean_= np.mean(scores_list)
            max_ = np.max(scores_list)

            #min_, mean_, max_ = round(min_, 3), round(mean_, 3), round(max_, 3),

            min_mean_max = []

            for m in (min_, mean_, max_):
                min_mean_max.append(m)

            self.__all_scores['line2'][train_test_set] = min_mean_max


    def _predict_probabilities(self, X_train, X_test, y_train):
        """
        This method calculates the probabilities of test set samples belogning each sentiment class using a model.

        :param X_train: scipy.sparse
        :param X_test: scipy.sparse
        :param y_train: list
        :param y_test: list
        :return: list
        """
        # Getting new model instance
        classifier = self._get_new_model_for_logical_selection()

        # Fitting
        classifier.fit(X_train, y_train)

        # Getting probabilities
        probabilities = classifier.predict_proba(X_test)

        return probabilities

    def _get_new_model_for_general_purpose(self):
        """
        Returns new classifier instance
        :return: OneVsRestClassifier
        """
        # model_for_general_purpose = SVC(C=1.0, kernel='poly', probability=True, degree=1.0, cache_size=250007)
        # model_for_general_purpose = OneVsRestClassifier(model_for_general_purpose)
        model_for_general_purpose = RandomForestClassifier(n_estimators=100)

        return model_for_general_purpose

    def _get_new_model_for_logical_selection(self):
        """
        Returns new classifier instance for logical selection
        :return:
        """
        # model_for_logical_selection = SVC(C=1.0, kernel='poly', probability=True, degree=1.0, cache_size=250007)
        # model_for_logical_selection = OneVsRestClassifier(model_for_logical_selection)
        model_for_logical_selection = RandomForestClassifier(n_estimators=100)

        return model_for_logical_selection

    def _get_sample_indexes_closest_to_decision_boundary(self, samples_probabilities):
        """
        Returns samples' indexes which are closest to decision boundary
        :param samples: list
        :return: list
        """
        standart_deviations = []
        for one_samples_probabilities in samples_probabilities:

            mean_of_samples_probabilities = np.std(one_samples_probabilities)
            standart_deviations.append(mean_of_samples_probabilities)

        # Finding elements which have minimum standart deviations
        np_array = np.array(standart_deviations)

        indices_of_minimum_stds = np_array.argsort()[:MOST_DISTINCT_SAMPLE_SIZE]
        # for indice in indices_of_minimum_stds:
        #     print(samples_probabilities[indice], standart_deviations[indice])
        return indices_of_minimum_stds

    def _plot_decision_boundary(self, X_train, X_test, y_train, y_test, highlighted_samples_indexes, plot_title):
        """
        Plots decision boundary of a point in line3 using dimensionality reduction with PCA(TruncatedSVD)
        :param X_train: scipy.sparse
        :param X_test: scipy.sparse
        :param y_train: list
        :param y_test: list
        :param highlighted_samples_indexes: list
        :param plot_title: string
        :return: void
        """

        # Creating classifiers
        classifier = self._get_new_model_for_general_purpose()
        svd = TruncatedSVD(n_components=2)

        # Encoding labeles to float
        y_train = self.__label_encoder.transform(y_train)
        y_test = self.__label_encoder.transform(y_test)

        # Splitting normal and highlighted samples
        probability_ranges = np.arange(X_test.shape[0])
        normal_samples_indexes = np.setdiff1d(probability_ranges, highlighted_samples_indexes)

        normal_samples_y = y_test[normal_samples_indexes]
        highlighted_samples_y = y_test[highlighted_samples_indexes]

        # Dimensionality reduction
        svd_X_train = svd.fit_transform(X_train)
        svd_X_test = svd.fit_transform(X_test)

        # Training the model
        classifier.fit(svd_X_train, y_train)

        x_min= min(svd_X_train[:, 0].min(), svd_X_test[:, 0].min()) - 2
        x_max = max(svd_X_train[:, 0].max(), svd_X_test[:, 0].max()) + 2

        y_min= min(svd_X_train[:, 1].min(), svd_X_test[:, 1].min()) - 2
        y_max = max(svd_X_train[:, 1].max(), svd_X_test[:, 1].max()) + 2


        xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01),
                             np.arange(y_min, y_max, 0.01))

        plt.figure(110)

        Z = classifier.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        plt.contourf(xx, yy, Z, cmap=plt.cm.Paired, alpha=0.8)

        # Train set
        #plt.scatter(svd_X_train[:, 0], svd_X_train[:, 1], c=y_train, cmap=plt.cm.Paired)

        # 150 samples from test set those are normal samples
        plt.scatter(svd_X_test[normal_samples_indexes][:, 0], svd_X_test[normal_samples_indexes][:, 1], c=normal_samples_y, cmap=plt.cm.Paired, s=5)

        # 50 samples from test set those are chosen
        plt.scatter(svd_X_test[highlighted_samples_indexes][:, 0], svd_X_test[highlighted_samples_indexes][:, 1], c=highlighted_samples_y, cmap=plt.cm.Paired, marker='D', s=50)

        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')

        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())

        info_text = "Reduced to 2 dims from %s dims. Dataset: %s\n" \
                    "Setup: %s. Explained Variance: %s" % (str(self.__feature_count), MODEL_NAME, plot_title, str(svd.explained_variance_ratio_.sum()))

        plt.title("PCA Projection on Decision Boundary of SVM.")

        plt.text(xx.mean()+2, yy.max()-0.5,  info_text, size=12, rotation=0.,
         ha="right", va="top",
         bbox=dict(boxstyle="square",
                   ec=(1., 0.5, 0.5),
                   fc=(1., 0.8, 0.8),
                   )
         )

        plt.show()

    def _choose_ale_samples_closest_to_decision_boundary(self, prob_X_train, prob_X_test, prob_y_train, prob_y_test):
        """

        :return:
        """
        # Find probabilities
        probabilities = self._predict_probabilities(prob_X_train, prob_X_test, prob_y_train)

        # Find closest samples to the decision boundary
        indexes_of_samples_closest_to_decision_boundary = self._get_sample_indexes_closest_to_decision_boundary(probabilities)

        samples_closest_to_decision_boundary_X = prob_X_test[indexes_of_samples_closest_to_decision_boundary]
        samples_closest_to_decision_boundary_y = prob_y_test[indexes_of_samples_closest_to_decision_boundary]

        return samples_closest_to_decision_boundary_X, samples_closest_to_decision_boundary_y

    def _ale_by_clustering_samples_with_original_features(self):
        """
        3244
        :return:
        """
        pass

    def _ale_by_clustering_samples_with_combined_features(self):
        """
        sinif olasiliklarini kullanarak
        :return:
        """
        pass

    def _combine_train_sets_and_run_classification(self, base_train_X, base_test_X, new_train_X, base_train_y, base_test_y, new_train_y):
        """

        :return:
        """
        # Find final train and test set
        final_X_train = base_train_X.toarray().tolist()
        final_X_train += new_train_X.toarray().tolist()
        final_sparse_X_train = sparse.csr_matrix(final_X_train)

        final_y_train = []
        final_y_train = base_train_y[:]
        final_y_train += new_train_y.tolist()

        # Test model and save the score
        acc_score = self._classify(final_sparse_X_train, base_test_X, final_y_train, base_test_y)

        return acc_score
