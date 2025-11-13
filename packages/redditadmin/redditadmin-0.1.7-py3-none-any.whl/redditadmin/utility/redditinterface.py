# -*- coding: utf-8 -*
from abc import ABCMeta, abstractmethod

from praw import Reddit


class RedditInterface(metaclass=ABCMeta):
    """
    Encapsulates tools to interface with the Reddit API
    """

    @property
    @abstractmethod
    def praw_reddit(self):
        """Retrieve the interface's PrawReddit instance"""
        ...


class RedditInterfaceImplementation(RedditInterface):

    def __init__(self, praw_reddit: Reddit):
        self.__prawReddit = praw_reddit

    @property
    def praw_reddit(self):

        return self.__prawReddit
