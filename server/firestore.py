from datetime import datetime
from firebase_admin import initialize_app
from firebase_admin import get_app
from firebase_admin.credentials import ApplicationDefault
from firebase_admin.firestore import client as firestore_client
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.cloud.firestore import DELETE_FIELD
from google.oauth2.credentials import Credentials
from json import loads
from logging import error
from logging import info
from logging import warning
from os import environ

# The scope to request for the Google Calendar API.
GOOGLE_CALENDAR_SCOPE = 'https://www.googleapis.com/auth/calendar.readonly'

# The token endpoint for Google OAuth.
GOOGLE_TOKEN_URI = 'https://oauth2.googleapis.com/token'

# The timestamp format used by oauth2client credential JSON.
OAUTH2CLIENT_EXPIRY_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class Firestore(object):
    """A wrapper around the Cloud Firestore database."""

    def __init__(self):
        # Only initialize Firebase once.
        try:
            get_app()
        except ValueError:
            initialize_app(ApplicationDefault(), {
                'projectId': environ['GOOGLE_CLOUD_PROJECT']
            })
        self._db = firestore_client()

    def _api_key(self, service):
        """Retrieves the API key for the specified service."""

        api_key = self._db.collection('api_keys').document(service).get()
        if not api_key.exists:
            raise DataError('Missing API key for: %s' % service)

        return api_key.get('api_key')

    def google_maps_api_key(self):
        """Retrieves the Google Maps API key."""

        return self._api_key('google_maps')

    def open_weather_api_key(self):
        """Retrieves the OpenWeather API key."""

        return self._api_key('open_weather')

    def google_calendar_secrets(self):
        """Loads the Google Calendar API secrets from the database."""

        clients = self._db.collection('oauth_clients')
        secrets = clients.document('google_calendar').get()
        if not secrets.exists:
            raise DataError('Missing Google Calendar secrets')

        return secrets.to_dict()

    def _google_calendar_credentials_from_json(self, credentials_json):
        """Loads Google Calendar credentials from current or legacy JSON."""

        info = loads(credentials_json)
        if info.get('invalid'):
            return None

        scopes = info.get('scopes') or [GOOGLE_CALENDAR_SCOPE]

        # Migrate JSON written by the deprecated oauth2client package.
        if 'access_token' in info:
            return Credentials(
                token=info.get('access_token'),
                refresh_token=info.get('refresh_token'),
                token_uri=info.get('token_uri') or GOOGLE_TOKEN_URI,
                client_id=info.get('client_id'),
                client_secret=info.get('client_secret'),
                scopes=scopes,
                expiry=self._parse_oauth2client_expiry(
                    info.get('token_expiry')))

        return Credentials.from_authorized_user_info(info, scopes=scopes)

    def _parse_oauth2client_expiry(self, expiry):
        """Parses oauth2client's naive UTC expiry timestamp."""

        if not expiry:
            return None

        return datetime.strptime(expiry, OAUTH2CLIENT_EXPIRY_FORMAT)

    def google_calendar_credentials(self, key):
        """Loads and refreshes Google Calendar API credentials."""

        # Look up the user from the key.
        user = self.user(key)
        if not user:
            return None

        # Load the credentials from storage.
        try:
            credentials_json = user.get('google_calendar_credentials')
        except KeyError:
            warning('Failed to load Google Calendar credentials.')
            return None

        # Use the valid credentials.
        try:
            credentials = self._google_calendar_credentials_from_json(
                credentials_json)
        except (TypeError, ValueError) as e:
            warning('Failed to parse Google Calendar credentials: %s' % e)
            self.delete_google_calendar_credentials(key)
            return None

        if credentials and credentials.valid:
            return credentials

        # Handle invalidation and expiration.
        if credentials and credentials.refresh_token:
            try:
                info('Refreshing Google Calendar credentials.')
                credentials.refresh(GoogleAuthRequest())
                self.update_google_calendar_credentials(key, credentials)
                return credentials
            except RefreshError as e:
                warning('Google Calendar refresh failed: %s' % e)

        # Credentials are missing or refresh failed.
        warning('Deleting Google Calendar credentials.')
        self.delete_google_calendar_credentials(key)
        return None

    def update_google_calendar_credentials(self, key, credentials):
        """Updates the users's Google Calendar credentials."""

        self.update_user(key, {
            'google_calendar_credentials': credentials.to_json()})

    def delete_google_calendar_credentials(self, key):
        """Deletes the users's Google Calendar credentials."""

        self.update_user(key, {'google_calendar_credentials': DELETE_FIELD})

    def user(self, key):
        """Retrieves the user snapshot matching the specified key."""

        user = self._user_reference(key).get()
        if not user.exists:
            warning('User not found.')
            return None

        return user

    def users(self, field_paths=None):
        """Returns an iterator over all users."""

        users = self._db.collection('users')
        if field_paths:
            users = users.select(field_paths)

        return users.stream()

    def _user_reference(self, key):
        """Retrieves the user reference matching the specified key."""

        return self._db.collection('users').document(key)

    def set_user(self, key, data):
        """Sets the data for the user matching the specified key."""

        # Use merge to only overwrite the specified data.
        self._user_reference(key).set(data, merge=True)

    def update_user(self, key, fields):
        """Updates the fields for the user matching the specified key."""

        user = self._user_reference(key)
        if not user.get().exists:
            error('User not found for update.')
            return

        user.update(fields)


class GoogleCalendarStorage(object):
    """Credentials storage for the Google Calendar API using Firestore."""

    def __init__(self, key):
        self._firestore = Firestore()
        self._key = key

    def get(self):
        """Loads credentials from Firestore."""

        return self._firestore.google_calendar_credentials(self._key)

    def put(self, credentials):
        """Saves credentials to Firestore."""

        self._firestore.update_google_calendar_credentials(self._key,
                                                           credentials)

    def refresh(self, credentials):
        """Refreshes credentials and saves the refreshed token."""

        credentials.refresh(GoogleAuthRequest())
        self.put(credentials)

    def delete(self):
        """Deletes credentials from Firestore."""

        self._firestore.delete_google_calendar_credentials(self._key)


class DataError(Exception):
    """An error indicating issues retrieving data."""

    pass
