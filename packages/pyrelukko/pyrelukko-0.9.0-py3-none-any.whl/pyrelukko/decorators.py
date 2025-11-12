"""
TBD
"""
import os
import time
from functools import wraps


# pylint: disable=too-many-arguments,too-many-positional-arguments
def retry(logger, exceptions, tries=4, delay=5,
          backoff=2.0, max_delay=None):
    """
    Retry calling the decorated function using an exponential backoff.
    https://www.calazan.com/retry-decorator-for-python-3/

    :param exceptions: The exception to check. may be a tuple of
     exceptions to check.
    :param tries: Number of times to try (not retry) before giving up.
    :param delay: Initial delay between retries in seconds.
    :param backoff: Backoff multiplier (e.g. value of 2 will double the delay
     each retry).
    :param max_delay: maximum value for delay
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            remaining_tries, retry_delay = tries, delay
            while remaining_tries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions:
                    remaining_tries -= 1
                    logger.warning('(%i/%i): Retrying in %i seconds...',
                        tries - remaining_tries,
                        tries,
                        retry_delay,
                    )
                    time.sleep(retry_delay)
                    if max_delay is not None:
                        retry_delay = min(retry_delay*backoff, max_delay)
                    else:
                        retry_delay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


SKIP_RELUKKO = {
    "id": "00000000-0000-0000-0000-000000000000",
    "lock_name": "WE TRUST YOU",
    "creator": "Dummy Dummy",
    "ip": "0.0.0.0",
    "expires_at": "1970-01-01T00:00:00Z",
    "created_at": "1970-01-01T00:00:00Z",
    "updated_at": "1970-01-01T00:00:00Z"
}


def skip_http_call():
    """
    Decorator for pyrlukko methods.

    It skips the actual method if the environment variable
    `RELUKKO_TRUST_ME_IT_IS_LOCKED` is set and returns instead a static lock
    dictionary or list with the same static lock dictionary.

    Useful when developing and the resource is for sure locked, e.g through the
    Web UI.
    """
    def deco_skip(f):

        @wraps(f)
        def f_skip(*args, **kwargs):
            if os.environ.get('RELUKKO_TRUST_ME_IT_IS_LOCKED'):
                if f.__name__ == "get_locks":
                    return [ SKIP_RELUKKO ]
                return SKIP_RELUKKO
            return f(*args, **kwargs)
        return f_skip  # true decorator
    return deco_skip
