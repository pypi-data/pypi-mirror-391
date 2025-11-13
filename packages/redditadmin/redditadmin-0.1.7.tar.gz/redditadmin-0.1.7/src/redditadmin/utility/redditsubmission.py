from abc import abstractmethod, ABCMeta

from praw.models import Submission


class RedditSubmission(metaclass=ABCMeta):
    """
    Encapsulates a submission
    """

    @property
    @abstractmethod
    def submission_id(self):
        ...


class RedditSubmissionImplementation(RedditSubmission):

    def __init__(self, submission_id):
        self.__submissionId = submission_id

    @property
    def submission_id(self):
        return self.__submissionId

    @classmethod
    def get_submission_from_id(
            cls, submission_id: str
    ) -> RedditSubmission:
        """
        Returns a RedditSubmission object from
        the provided submission_id
        """
        return RedditSubmissionImplementation(submission_id)

    @classmethod
    def get_submission_from_praw_submission(
            cls, praw_submission: Submission
    ) -> RedditSubmission:
        """
        Returns a RedditSubmission object from
        the provided PRAW submission
        """
        return RedditSubmissionImplementation(praw_submission.id)
