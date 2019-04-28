from cachetools import cached
from cachetools import TTLCache
from firebase_admin import _apps as firebase_apps
from firebase_admin import initialize_app
from firebase_admin.credentials import ApplicationDefault
from firebase_admin.firestore import client as firestore_client
from googleapiclient.http import build_http
from google.cloud.firestore import DELETE_FIELD
from logging import error
from logging import info
from logging import warning
from oauth2client.client import HttpAccessTokenRefreshError
from oauth2client.client import OAuth2Credentials
from oauth2client.client import Storage
from os import environ
from threading import Lock


class Firestore:
    """A wrapper around the Cloud Firestore database."""

    def __init__(self):
        # Only initialize Firebase once.
        if not len(firebase_apps):
            initialize_app(ApplicationDefault(), {
                "projectId": environ["GOOGLE_CLOUD_PROJECT"],
            })
        self.db = firestore_client()

    def _api_key(self, service):
        """Retrieves the API key for the specified service."""

        service = self.db.collection("api_keys").document(service).get()
        if not service.exists:
            return None

        return service.get("api_key")

    def google_maps_api_key(self):
        """Retrieves the Google Maps API key."""

        return self._api_key("google_maps")

    def dark_sky_api_key(self):
        """Retrieves the Dark Sky API key."""

        return self._api_key("dark_sky")

    def google_calendar_secrets(self):
        """Loads the Google Calendar API secrets from the database."""

        clients = self.db.collection("oauth_clients")
        secrets = clients.document("google_calendar").get()

        return secrets.to_dict()

    def google_calendar_credentials(self, key):
        """Loads and refreshes Google Calendar API credentials."""

        # Look up the user from the key.
        user = self.user(key)
        if not user:
            return None

        # Load the credentials from storage.
        try:
            json = user.get("google_calendar_credentials")
        except KeyError:
            warning("Failed to load Google Calendar credentials.")
            return None

        # Use the valid credentials.
        credentials = OAuth2Credentials.from_json(json)
        if credentials and not credentials.invalid:
            return credentials

        # Handle invalidation and expiration.
        if credentials and credentials.access_token_expired:
            try:
                info("Refreshing Google Calendar credentials.")
                credentials.refresh(build_http())
                return credentials
            except HttpAccessTokenRefreshError as e:
                warning("Google Calendar refresh failed: %s" % e)

        # Credentials are missing or refresh failed.
        warning("Deleting Google Calendar credentials.")
        self.delete_google_calendar_credentials(key)
        return None

    def update_google_calendar_credentials(self, key, credentials):
        """Updates the users's Google Calendar credentials."""

        self.update_user(key, {
            "google_calendar_credentials": credentials.to_json()})

    def delete_google_calendar_credentials(self, key):
        """Deletes the users's Google Calendar credentials."""

        self.update_user(key, {"google_calendar_credentials": DELETE_FIELD})

    def user(self, key):
        """Retrieves the user matching the specified key."""

        user = self.db.collection("users").document(key).get()
        if not user.exists:
            error("User not found.")
            return None

        return user

    def set_user(self, key, data):
        """Sets the data for the user matching the specified key."""

        user = self.db.collection("users").document(key)
        user.set(data)

    def update_user(self, key, fields):
        """Updates the fields for the user matching the specified key."""

        user = self.db.collection("users").document(key)
        if not user.get().exists:
            error("User not found for update.")
            return

        user.update(fields)


class GoogleCalendarStorage(Storage):
    """Credentials storage for the Google Calendar API using Firestore."""

    def __init__(self, key):
        super(GoogleCalendarStorage, self).__init__(lock=Lock())
        self.firestore = Firestore()
        self.key = key

    def locked_get(self):
        """Loads credentials from Firestore and attaches this storage."""

        credentials = self.firestore.google_calendar_credentials(self.key)
        if not credentials:
            return None
        credentials.set_store(self)
        return credentials

    def locked_put(self, credentials):
        """Saves credentials to Firestore."""

        self.firestore.update_google_calendar_credentials(self.key,
                                                          credentials)

    def locked_delete(self):
        """Deletes credentials from Firestore."""

        self.firestore.delete_google_calendar_credentials(self.key)
