from cachetools import cached
from cachetools import TTLCache
from firebase_admin import _apps as firebase_apps
from firebase_admin import initialize_app
from firebase_admin.credentials import ApplicationDefault
from firebase_admin.firestore import client as firestore_client
from os import environ


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

    def user(self, key):
        """Retrieves the user matching the specified key."""

        user = self.db.collection("users").document(key).get()
        if not user.exists:
            return None

        return user

    def update_user(self, key, data):
        """Replaces the data for the user matching the specified key."""

        user = self.db.collection("users").document(key)
        user.set(data)

        return user.get()
