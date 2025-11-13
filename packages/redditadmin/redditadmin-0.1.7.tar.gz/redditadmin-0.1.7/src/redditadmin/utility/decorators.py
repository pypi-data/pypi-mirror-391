"""
Module containing utility decorators which may
be used by program
"""

import functools
import time

from prawcore.exceptions import RequestException, ServerError


def consumestransientapierrors(_execute_function=None, *, timeout: int = 30):
    """
    Consumes common transient errors which may
    occur while connecting to the Reddit API during
    the running of the provided program
    """

    def subsuming_function(execute_function):

        @functools.wraps(execute_function)
        def wrapper(*args, **kwargs):
            try:
                program_logger = getattr(args[0], '_programLogger', None)
            except IndexError:
                program_logger = None
            while True:
                try:
                    function_value = execute_function(*args, **kwargs)
                    return function_value
                # Handle for problems connecting to the Reddit API
                except (RequestException, ServerError) as ex:
                    message = "Failed to connect to the Reddit API: {}".format(
                                ex.args
                    )
                    if program_logger:
                        program_logger.warning(
                            message
                        )
                    else:
                        print(message)
                    time.sleep(timeout)
        return wrapper

    # Handle if decorator is called with arguments
    if _execute_function is None:
        return subsuming_function
    else:
        return subsuming_function(_execute_function)
