from praw.models import Submission
from pytest_mock import MockFixture

from ..redditsubmission import RedditSubmissionImplementation


class TestRedditSubmissionImplementation:

    def test_init(self):
        submission_id = "KMLKcalskc"
        reddit_submission = RedditSubmissionImplementation(
            submission_id=submission_id
        )

        assert reddit_submission.submission_id == submission_id

    def test_get_submission_from_id(self):
        submission_id = "jndakjna"
        reddit_submission = RedditSubmissionImplementation.get_submission_from_id(
            submission_id=submission_id
        )

        assert reddit_submission.submission_id == submission_id

    def test_get_submission_from_praw_submission(self, mocker: MockFixture):
        submission_id = "ladidididaaaa"
        praw_submission = mocker.Mock(spec=Submission)
        praw_submission.configure_mock(**{
            "id": submission_id
        })
        reddit_submission = RedditSubmissionImplementation.get_submission_from_praw_submission(
            praw_submission=praw_submission
        )

        assert reddit_submission.submission_id == submission_id
