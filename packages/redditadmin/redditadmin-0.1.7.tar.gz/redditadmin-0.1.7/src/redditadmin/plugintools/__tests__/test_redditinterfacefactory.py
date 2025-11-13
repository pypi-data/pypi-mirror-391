import pytest
from pytest_mock import MockFixture

from ..redditinterfacefactory import DefaultRedditInterfaceFactory
from ...utility.botcredentials import BotCredentials, InvalidBotCredentialsError


class TestDefaultRedditInterfaceFactory:

    def test_faulty_initialization(self, mocker: MockFixture, monkeypatch):
        mocked_bot_credentials = mocker.Mock(spec=BotCredentials)
        mocker.patch('src.redditadmin.plugintools.redditinterfacefactory.is_reddit_authenticated',
                     lambda bot_credentials: False)
        with pytest.raises(InvalidBotCredentialsError):
            DefaultRedditInterfaceFactory(mocked_bot_credentials)

    def test_proper_initialization(self, mocker: MockFixture):
        mocked_bot_credentials = mocker.Mock(spec=BotCredentials)
        mocker.patch('src.redditadmin.plugintools.redditinterfacefactory.is_reddit_authenticated',
                     lambda bot_credentials: True)
        assert DefaultRedditInterfaceFactory(mocked_bot_credentials)
