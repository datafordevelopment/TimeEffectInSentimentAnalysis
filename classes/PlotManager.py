# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from config import *
from matplotlib import pyplot as plt
from matplotlib.patches import Patch

from helpers.GeneralHelpers import GeneralHelpers

class PlotManager:
    """
    This class does the necessary works for visualizing data
    """
    def __init__(self):
        self.__helper = GeneralHelpers()
        self.__colors = ['r', 'b', 'y', 'm', 'g', 'c', 'k']
        self.__years = ('2012', '2013', '2014', '2015')

    def plot_years_scores_from_root_directory(self, root_dir):
        """
        Plots __years' scores for given classifiers and mean of them
        :param root_dir: string, root directory to scan
        :return: void
        """
        bar_width = 0.10

        # Getting scores from helper
        years_classifier_scores_list = []
        years_classifier_scores_dict = self.__helper.get_accuracy_scores_for_years_from_root_dir(root_dir)

        # Making them lists
        for year, classifiers_scores in years_classifier_scores_dict.iteritems():
            years_classifier_scores_list.append(classifiers_scores.values())

        years_classifier_scores_list = np.array(years_classifier_scores_list)
        classifier_names = years_classifier_scores_dict['2012'].keys()

        indexes = np.arange(len(years_classifier_scores_dict.keys()))  # [0,1,2,3] +

        # Iterating over J48 for 2012, 2013, 2014, 2015, MEAN for 2012, 2013, 2014, 2015 an so on..
        for iteration_number, (color_name, classifier_name, classifier_scores) in enumerate(zip(self.__colors, classifier_names, years_classifier_scores_list.T)):
            bar_offset = indexes + (iteration_number * bar_width)
            plt.bar(bar_offset, classifier_scores, bar_width, color=color_name, label=classifier_name)

        plt.xlabel('Years')
        plt.ylabel('Scores %')
        plt.title('Scores by year and classifier(' + MODEL_NAME + ', CV=4)')
        plt.xticks(indexes + bar_width, self.__years)
        plt.legend(loc=4)
        plt.show()

    def plot_2012_vs_rest(self, root_dir):
        """
        Plots 2012 vs rest
        :param root_dir: string
        :return: void
        """
        all_accuracy_scores = self.__helper.get_log_files_stats(root_dir)
        """
        Example accuracy scores:
        {
            'SMO':{
                2013: [62.79, 66.67, 50.0, 70.45, 57.14, 60.0, 64.29, 66.67, 62.79, 73.17, 57.14, 66.67],
                2014: [65.45, 58.97, 54.35, 72.09, 47.62, 66.67, 71.43, 66.67, 57.78, 64.44, 71.43, 59.26],
                2015: [62.79, 57.14, 63.16, 62.5, 59.26, 67.27, 61.76, 66.67, 68.63]
            },
            'IB1': {
                2013: [37.21, 40.48, 38.1, 43.18, 45.24, 47.5, 45.24, 35.71, 32.56, 24.39, 28.57, 51.28],
                2014: [38.18, 43.59, 41.3, 39.53, 47.62, 50.0, 33.33, 44.44, 26.67, 24.44, 40.48, 37.04],
                2015: [37.21, 41.07, 43.86, 39.29, 51.85, 30.91, 39.71, 26.32, 45.1]
            }
            ...
            ...
            ...
        }
        """
        self._plot_2012_vs_rest_monthly(all_accuracy_scores)
        self._plot_2012_vs_rest_yearly(all_accuracy_scores)

    def _plot_2012_vs_rest_monthly(self, all_accuracy_scores):
        """

        :param all_accuracy_scores:
        :return:
        """

        date_ranges = pd.date_range(start='1/1/2013', periods=33, freq='M')
        date_ranges = np.array([date_obj.strftime('%b-%y') for date_obj in date_ranges])

        xs = date_ranges

        for iteration_number, classifier_scores in enumerate(all_accuracy_scores.values()):
            ys = []
            fig = plt.figure(iteration_number)
            for year, year_scores in classifier_scores.iteritems():
                ys += year_scores

            xs = np.arange(1, 34, 1)

            plt.xlabel("Months")
            plt.ylabel("Scores%")
            plt.title(all_accuracy_scores.keys()[iteration_number])
            print(xs,ys)
            plt.plot(xs, ys)

    def _plot_2012_vs_rest_yearly(self, all_accuracy_scores):
        """

        :param all_accuracy_scores:
        :return:
        """
        date_ranges = pd.date_range(start='1/1/2013', periods=3, freq='365D')
        date_ranges = np.array([date_obj.strftime('%y') for date_obj in date_ranges])

        xs = date_ranges
        yearly_scores = {}


        fig, ax = plt.subplots()
        names_of_classifiers = all_accuracy_scores.keys()

        for iteration_number, classifier_scores in enumerate(all_accuracy_scores.values()):
            ys = []
            for year, year_scores in classifier_scores.iteritems():
                ys.append(np.mean(year_scores))

            plt.xlabel('Years')
            plt.ylabel('Scores %')
            plt.title('Scores by year and classifier(' + MODEL_NAME + ', train=2012, test=2013, 2014, 2015)')
            ax.set_xticklabels(xs)
            plt.xticks(rotation=90)
            ax.plot(xs, ys, self.__colors[iteration_number], label=names_of_classifiers[iteration_number])
            plt.legend()
        plt.show()

    def plot_top_feature_frequencies_in_years(self, years_features_counts):
        """
        Plots top features' frequencies in __years
        :return: void
        """

        plot_feature_counts = {}
        bar_width = 0.20

        for feature_name in INFO_GAIN_ATTRIBUTES:
            if not feature_name in plot_feature_counts:
                plot_feature_counts[feature_name] = []

            f_key = feature_name.decode('utf-8')

            for year in self.__years:
                if not f_key in years_features_counts[year]:
                    years_features_counts[year][f_key] = 0

            plot_feature_counts[feature_name] = [years_features_counts["2012"][f_key],
                                                  years_features_counts["2013"][f_key],
                                                  years_features_counts["2014"][f_key],
                                                  years_features_counts["2015"][f_key]
                                                ]
        print(plot_feature_counts)

        indexes = np.arange(len(plot_feature_counts.keys()))

        for first_iteration_number, (feature_name, feature_counts) in enumerate(plot_feature_counts.iteritems()):
            for second_iteration_number, (color, feature_count) in enumerate(zip(self.__colors, feature_counts)):
                x_coord = first_iteration_number + (second_iteration_number*bar_width)
                plt.bar(x_coord, feature_count, bar_width, color=color)

        xticks = [key.decode('utf-8') for key in plot_feature_counts.keys()]

        plt.xlabel('Features')
        plt.ylabel('Frequencies in __years')
        plt.title('InfoGain features by year and features(' + MODEL_NAME + ')')
        plt.xticks(indexes + bar_width*2, xticks)

        handles = []
        for idx, (year, color) in enumerate(zip(self.__years, self.__colors)):
            patch = Patch(color=color, label=year)
            handles.append(patch)

        plt.legend(loc=1, handles=handles)
        plt.show()
