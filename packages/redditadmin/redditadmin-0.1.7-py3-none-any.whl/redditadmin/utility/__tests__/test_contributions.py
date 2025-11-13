from typing import Union

from praw.models import Submission, Comment
from pytest_mock import MockFixture

from ..contributions import is_removed


class TestContributions:

    def test_is_removed(self, mocker: MockFixture):
        test_contribution_1 = mocker.Mock(spec=Union[Submission, Comment])
        test_contribution_2 = mocker.Mock(spec=Union[Submission, Comment])
        test_contribution_3 = mocker.Mock(spec=Union[Submission, Comment])
        test_contribution_4 = mocker.Mock(spec=Union[Submission, Comment])

        test_contribution_1.configure_mock(**{
            "author": "[Deleted]",
            "banned_by": None
        })
        test_contribution_2.configure_mock(**{
            "author": "UserX",
            "banned_by": "ModeratorX"
        })
        test_contribution_3.configure_mock(**{
            "banned_by": None
        })
        test_contribution_4.configure_mock(**{
            "author": "UserY",
            "banned_by": None,
        })

        assert is_removed(test_contribution_1)
        assert is_removed(test_contribution_2)
        assert is_removed(test_contribution_3)
        assert not is_removed(test_contribution_4)
