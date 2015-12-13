# -*- coding: utf-8 -*-

from config import *
from classes.Main import Main
from helpers.Preprocessor import Preprocessor

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
    #main.extract_features_and_generate_arff(n=3, analyzer='char', year='2012')

    """
    Example code to plot __years' scores
    """
    #root path, ../DataSet-Logs/Word/YearsOnly/TTNet/
    root_path_for_years_itself = PROJECT_ROOT_DIRECTORY + DATASET_LOGS_DIR_NAME + FEATURE_TYPE+\
                                LOGS_YEARS_ITSELF_DIR_NAME+MODEL_NAME+'/'
    main.plot_years_scores(root_path_for_years_itself)