from abc import ABCMeta, abstractmethod

import praw

from ..utility.botcredentials import BotCredentials, InvalidBotCredentialsError
from ..utility.miscellaneous import is_reddit_authenticated
from ..utility.redditinterface import RedditInterface, RedditInterfaceImplementation


class RedditInterfaceFactory(metaclass=ABCMeta):
    """Factory for RedditInterface objects"""

    @abstractmethod
    def get_reddit_interface(self) -> RedditInterface:
        """Retrieve new Reddit Interface"""
        ...


class DefaultRedditInterfaceFactory(RedditInterfaceFactory):

    def __init__(
            self,
            bot_credentials: BotCredentials
    ):
        praw_reddit = praw.Reddit(
            user_agent=bot_credentials.user_agent,
            client_id=bot_credentials.client_id,
            client_secret=bot_credentials.client_secret,
            username=bot_credentials.username,
            password=bot_credentials.password
        )
        if not is_reddit_authenticated(praw_reddit):
            raise InvalidBotCredentialsError

        self.__botCredentials = bot_credentials

    def get_reddit_interface(self):

        bot_credentials = self.__botCredentials
        praw_reddit = praw.Reddit(
            user_agent=bot_credentials.user_agent,
            client_id=bot_credentials.client_id,
            client_secret=bot_credentials.client_secret,
            username=bot_credentials.username,
            password=bot_credentials.password
        )
        return RedditInterfaceImplementation(praw_reddit)
