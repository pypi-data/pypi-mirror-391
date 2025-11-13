from praw import Reddit
from praw.models import User
from pytest_mock import MockFixture

from ..miscellaneous import is_reddit_authenticated


class TestMiscellaneous:

    def test_is_reddit_authenticated(self, mocker: MockFixture):

        reddit_mock_1 = mocker.Mock(spec=Reddit, user=mocker.Mock(spec=User))
        reddit_mock_2 = mocker.Mock(spec=Reddit, user=mocker.Mock(spec=User))

        reddit_mock_1.user.me.return_value = "Guy123"
        reddit_mock_2.user.me.return_value = None

        assert is_reddit_authenticated(reddit_mock_1)
        assert not is_reddit_authenticated(reddit_mock_2)
