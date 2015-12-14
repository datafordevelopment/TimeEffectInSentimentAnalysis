# -*- coding: utf-8 -*-

from config import *
import collections
from classes.Main import Main

if __name__ == "__main__":
    main = Main()

    """
    Example code to import tweets
    """
    #file_path = os.path.realpath(PROJECT_ROOT_DIRECTORY+DATASET_TXT_DIR_NAME+"TTNetTweets2012.txt")
    #main.retrieve_tweets(file_path)



    """
    Example code to generate arff file with given feature parameters
    """
    #main.extract_features_and_generate_arff(n=1, analyzer='word', year='2012')



    """
    Example code to plot years' scores
    """
    # root path, ../DataSet-Logs/Word/YearsOnly/TTNet/
    #root_path_for_years_itself = PROJECT_ROOT_DIRECTORY + DATASET_LOGS_DIR_NAME + FEATURE_TYPE+LOGS_YEARS_ITSELF_DIR_NAME+MODEL_NAME+'/'
    #main.plot_years_scores(root_path_for_years_itself)



    """
    Example code to plot 2012 vs rest
    """
    #root_path_for_2012_vs_rest = PROJECT_ROOT_DIRECTORY + DATASET_LOGS_DIR_NAME + FEATURE_TYPE + LOGS_2012_VS_REST + MODEL_NAME
    #main.plot_2012_vs_rest(root_path_for_2012_vs_rest)



    """
    Example code to plot top info gain features' frequencies in years.
    """
    #main.plot_top_feature_frequencies_in_years()



    """
    Example code to plot years' intersection scores with each other
    """
    #main.plot_years_intersection_scores()



    """
    Example code to make experiment
    """
    print("Initalizing.")
    all_line_scores_of_all_experiments = main.run_experiment_with_scikit_learn(n=1, analyzer='word')

    for line_name, line_points in all_line_scores_of_all_experiments.iteritems():
        all_line_scores_of_all_experiments[line_name] = collections.OrderedDict(sorted(line_points.items()))

    main.plot_all_experiment_results_with_scikit_learn(all_line_scores_of_all_experiments)
