from flask import request
from flask import url_for
from functools import wraps
from googleapiclient.http import build_http
from logging import error
from oauth2client.client import HttpAccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from re import compile as re_compile

from firestore import Firestore
from firestore import GoogleCalendarStorage
from response import forbidden_response
from response import settings_response
from response import text_response

# The scope to request for the Google Calendar API.
GOOGLE_CALENDAR_SCOPE = 'https://www.googleapis.com/auth/calendar.readonly'

# The URL where Google Calendar access can be revoked.
ACCOUNT_ACCESS_URL = 'https://myaccount.google.com/permissions'

# The regular expression a user key has to match.
KEY_PATTERN = re_compile('^[a-zA-Z0-9]{12}$')

# The time in milliseconds to return in an unauthorized next request.
NEXT_RETRY_DELAY_MILLIS = 5 * 60 * 1000  # 5 minutes


def next_retry_response():
    """Creates a response for a next request with a fixed retry time."""

    return text_response(str(NEXT_RETRY_DELAY_MILLIS))


def _oauth_url():
    """Creates the URL handling OAuth redirects."""

    return url_for('oauth', _external=True)


def _valid_key(key):
    """Checks if a user key's format is as expected."""

    return KEY_PATTERN.fullmatch(key)


def validate_key(func):
    """A decorator for Flask route functions to enforce valid keys."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _valid_key(kwargs['key']):
            return forbidden_response()

        return func(*args, **kwargs)

    return wrapper


def user_auth(image_response=None, bad_response=forbidden_response):
    """A decorator for Flask route functions to enforce user authentication."""

    firestore = Firestore()

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Look for a key debug request argument first.
                key = request.args['key']
            except KeyError:
                # Otherwise, expect a basic access authentication header.
                authorization = request.authorization
                if not authorization:
                    return bad_response()
                key = authorization['password']

            # Disallow malformed keys.
            if not _valid_key(key):
                return bad_response()

            # Look up the user from the key.
            user = firestore.user(key)
            if not user:
                if image_response:
                    # For image requests, start the new user flow.
                    return settings_response(key, image_response)
                else:
                    # Otherwise, return a forbidden response.
                    return bad_response()

            # Inject the key and user into the function arguments.
            kwargs['key'] = key
            kwargs['user'] = user
            kwargs['size'] = (
                request.args.get('width', default=640, type=int),
                request.args.get('height', default=384, type=int)
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _google_calendar_flow(key):
    """Creates the OAuth flow."""

    secrets = Firestore().google_calendar_secrets()
    return OAuth2WebServerFlow(client_id=secrets['client_id'],
                               client_secret=secrets['client_secret'],
                               scope=GOOGLE_CALENDAR_SCOPE,
                               state=key,
                               redirect_uri=_oauth_url())


def google_calendar_step1(key):
    """Creates the URL for the first OAuth step."""

    # The user key is passed through the flow as state.
    flow = _google_calendar_flow(key)
    return flow.step1_get_authorize_url(state=key)


def _google_calendar_step2(key, code):
    """Creates the URL for the second OAuth step."""

    flow = _google_calendar_flow(key)
    return flow.step2_exchange(code=code)


def oauth_step2(key, scope, code):
    """Exchanges and saves the OAuth credentials."""

    # Use scope-specific token exchange and storage steps.
    if scope == GOOGLE_CALENDAR_SCOPE:
        credentials = _google_calendar_step2(key, code)
        storage = GoogleCalendarStorage(key)
        credentials.set_store(storage)
        try:
            credentials.refresh(build_http())
        except HttpAccessTokenRefreshError as e:
            storage.delete()
            error('Token refresh error: %s' % e)
    else:
        error('Unknown OAuth scope: %s' % scope)
