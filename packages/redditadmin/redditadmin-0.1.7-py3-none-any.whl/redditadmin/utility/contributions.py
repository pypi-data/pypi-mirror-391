"""
Module providing various utility methods
for submissions and comments
"""
from typing import List, Union

from praw import Reddit
from praw.models import Submission, Comment


# TODO: Unpushshift
def retrieve_submissions_from_subreddit(
        reddit: Reddit,
        subreddit_name: str,
        from_time: str,
        filters: List[str]
) -> List[Submission]:
    """
    Retrieves all submissions from a given subreddit
    after the provided time containing only filtered info
    """
    # return list(
    #     reddit.subreddit.search_submissions(
    #         subreddit=subredditName,
    #         after=fromTime,
    #         filter=filters
    #     )
    # )
    raise NotImplementedError


def retrieve_select_submissions(
        praw_reddit: Reddit,
        submission_ids: List[str]
) -> List[Submission]:
    """
    Retrieves submissions with the given submissionIds
    """

    submissions = []

    for submissionId in submission_ids:
        submissions.append(
            praw_reddit.submission(submissionId)
        )
    return submissions


def is_removed(
        contribution: Union[Submission, Comment]
) -> bool:
    """
    Checks if provided comment or
    submission is removed
    """

    try:
        author = contribution.author
    except AttributeError:
        author = None
    return author is None or author == '[Deleted]' or \
        contribution.banned_by is not None
