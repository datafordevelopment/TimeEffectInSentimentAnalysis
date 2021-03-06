# -*- coding: utf-8 -*-
# encoding: utf-8

import os
import re
import json
import string
import difflib

class Preprocessor:
    """
    This is a helper classin preprocessing step which removes irrelevant information from tweets
    """
    def __init__(self):
        """
        Constructor
        :return: Preprocessor
        """
        self.regexpForURLs = 'http[s]?:?/?/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|\
                              [!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        self.compiledDigitRegex = re.compile('\d')
        self.compiledAlphanumericRegex = re.compile('\W+', re.UNICODE)
        self.compiledRTRegex = re.compile(r'RT')

        eyes, noses, mouths = r':;8BX=', r'-~\'^', r')\(/\|ODP'
        self.pattern1 = "[%s][%s]?[%s]" % tuple(map(re.escape, [eyes, noses, mouths]))

    def clean_all(self, tweet):
        """
        Makes necessary function calls to remove all irrelevant information from a given tweet's text.
        :param tweet: String
        :return: String
        """
        tweet = self.clean_urls(tweet)
        tweet = self.clean_hashtags(tweet)
        tweet = self.clean_mentions(tweet)
        tweet = self.clean_emojis_and_smileys(tweet)
        tweet = self.clean_unnecessary_characters(tweet)
        tweet = self.clean_reserved_words(tweet)

        return tweet

    def clean_unnecessary_characters(self, tweet):
        """
        Removes some unnecessary characters such as punctutational chars
        :param tweet: String
        :return: String
        """
        tweet = tweet.lstrip("\"").rstrip("\"")
        tweet = re.sub(self.compiledAlphanumericRegex, ' ', tweet)
        tweet = tweet.replace('_', ' ')
        return tweet

    def clean_hashtags(self, tweet):
        """
        Removes hashtags from a tweet's text
        :param tweet: String
        :return: String
        """
        self.hashtags = [tag.strip('#') for tag in tweet.split()
                         if tag.startswith('#')]

        for hashtag in self.hashtags:
            tweet = tweet.replace('#'+hashtag, '')

        tweet = self.clean_unnecessary_whitespaces(tweet)
        return tweet

    def clean_urls(self, tweet):
        """
        Removes urls from a tweet's text
        :param tweet:
        :return:
        """
        self.urls = re.findall(self.regexpForURLs, tweet)

        for url in self.urls:
            tweet = tweet.replace(url, '')

        tweet = self.clean_unnecessary_whitespaces(tweet)
        return tweet

    def clean_unnecessary_whitespaces(self, tweet):
        """
        Replaces multiple whitespaces with one
        :param tweet: String
        :return: String
        """
        tweet = ' '.join(tweet.split())

        return tweet

    def clean_mentions(self, tweet):
        """
        Removes mentions from a tweet's text
        :param tweet: String
        :return: String
        """
        self.mentions = [tag.strip('@') for tag in tweet.split() if tag.startswith('@')]

        for mention in self.mentions:
            tweet = tweet.replace('@'+mention, '')

        tweet = self.clean_unnecessary_whitespaces(tweet)

        return tweet

    def clean_reserved_words(self, tweet):

        tweet = re.sub(self.compiledRTRegex, '', tweet)
        tweet = self.clean_unnecessary_whitespaces(tweet)
        return tweet

    def clean_emojis_and_smileys(self, tweet):
        """
        Removes emojis and smileys from a tweet's text
        :param tweet: String
        :return: String
        """
        smileys = re.findall(self.pattern1, tweet)

        for smiley in smileys:
            tweet = tweet.replace(smiley, '')

        try:
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')

        except re.error:
            # UCS-2 build
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        tweet = highpoints.sub(u'', tweet)

        tweet =  self.clean_unnecessary_whitespaces(tweet)
        return tweet

    def string_contains_digits(self, string):
        """
        Checks if string contains digits
        :param string: String
        :return: bool
        """
        return bool(self.compiledDigitRegex.search(string))

