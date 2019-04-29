from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from googleapiclient.http import build_http
from logging import error
from logging import exception
from oauth2client.client import HttpAccessTokenRefreshError
from pytz import common_timezones
from time import time

from artwork import Artwork
from auth import ACCOUNT_ACCESS_URL
from auth import google_calendar_step1
from auth import google_calendar_step2
from auth import next_retry_response
from auth import settings_url
from auth import user_auth
from auth import validate_key
from auth import verify_scope
from city import City
from commute import Commute
from firestore import Firestore
from firestore import GoogleCalendarStorage
from google_calendar import GoogleCalendar
from response import epd_response
from response import png_response
from response import text_response
from schedule import Schedule

# The URL of the Medium story about Accent.
INFO_URL = "https://medium.com/@maxbraun/meet-accent-352cfa95813a"

# The template for editing user data.
HELLO_TEMPLATE = "hello.html"

app = Flask(__name__)


@app.route("/artwork")
@user_auth(image_response=png_response)
def artwork(key=None, user=None):
    """Responds with a PNG version of the artwork image."""

    artwork = Artwork(user)
    image = artwork.image()
    return png_response(image)


@app.route("/city")
@user_auth(image_response=png_response)
def city(key=None, user=None):
    """Responds with a PNG version of the city image."""

    city = City(user)
    image = city.image()
    return png_response(image)


@app.route("/commute")
@user_auth(image_response=png_response)
def commute(key=None, user=None):
    """Responds with a PNG version of the commute image."""

    commute = Commute(user)
    image = commute.image()
    return png_response(image)


@app.route("/calendar")
@user_auth(image_response=png_response)
def calendar(key=None, user=None):
    """Responds with a PNG version of the calendar image."""

    calendar = GoogleCalendar(key, user)
    image = calendar.image()
    return png_response(image)


@app.route("/png")
@user_auth(image_response=png_response)
def png(key=None, user=None):
    """Responds with a PNG version of the scheduled image."""

    schedule = Schedule(key, user)
    image = schedule.image()
    return png_response(image)


@app.route("/epd")
@user_auth(image_response=epd_response)
def epd(key=None, user=None):
    """Responds with an e-paper display version of the scheduled image."""

    schedule = Schedule(key, user)
    image = schedule.image()
    return epd_response(image)


@app.route("/next")
@user_auth(bad_response=next_retry_response)
def next(key=None, user=None):
    """Responds with the milliseconds until the next image."""

    schedule = Schedule(key, user)
    milliseconds = schedule.delay()
    return text_response(str(milliseconds))


@app.route("/")
def root():
    """Redirects to the Medium story about Accent."""

    return redirect(INFO_URL)


@app.route("/hello/<key>", methods=["GET"])
@validate_key
def hello_get(key):
    """Responds with a form for editing user data."""

    # Look up any existing user data.
    firestore = Firestore()
    calendar_credentials = GoogleCalendarStorage(key).get()

    # Force a Google Calendar credentials refresh to get the latest status.
    if calendar_credentials:
        try:
            calendar_credentials.refresh(build_http())
        except HttpAccessTokenRefreshError:
            calendar_credentials = None

    calendar_connected = calendar_credentials is not None
    return render_template(HELLO_TEMPLATE, key=key, user=firestore.user(key),
                           calendar_connected=calendar_connected,
                           calendar_connect_url=google_calendar_step1(key),
                           calendar_disconnect_url=ACCOUNT_ACCESS_URL,
                           time_zones=common_timezones)


@app.route("/hello/<key>", methods=["POST"])
@validate_key
def hello_post(key):
    """Saves user data and responds with the updated form."""

    form = request.form
    firestore = Firestore()
    calendar_credentials = GoogleCalendarStorage(key).get()

    # Build the schedule from the form data, dropping any empty entries.
    list_form = form.to_dict(flat=False)
    schedule_form = zip(list_form["schedule_name"],
                        list_form["schedule_start"],
                        list_form["schedule_image"])
    schedule = [{"name": name, "start": start, "image": image}
                for name, start, image in schedule_form
                if name and start and image]

    # Update the existing user data or create a new one.
    firestore.set_user(key, {
        "time_zone": form["time_zone"],
        "home": form["home"],
        "work": form["work"],
        "travel_mode": form["travel_mode"],
        "schedule": schedule})
    if calendar_credentials:
        firestore.update_user(key, {
            "google_calendar_credentials": calendar_credentials.to_json()})
    user = firestore.user(key)

    calendar_connected = calendar_credentials is not None
    return render_template(HELLO_TEMPLATE, key=key, user=user,
                           calendar_connected=calendar_connected,
                           calendar_connect_url=google_calendar_step1(key),
                           calendar_disconnect_url=ACCOUNT_ACCESS_URL,
                           time_zones=common_timezones)


@app.route("/oauth")
def oauth():
    """Handles any OAuth flow redirects."""

    # Always redirect back to the settings page.
    key = request.args.get("state")
    settings = redirect(settings_url(key))

    # Handle any errors, notable the user declining.
    oauth_error = request.args.get("error")
    if oauth_error:
        error("OAuth error: %s" % oauth_error)
        return settings

    # Verify the the scope is as expected.
    scope = request.args.get("scope")
    if not verify_scope(scope):
        error("Unknown OAuth scope: %s" % scope)
        return settings

    # Exchange and save the OAuth credentials.
    code = request.args.get("code")
    credentials = google_calendar_step2(key, code)
    credentials.set_store(GoogleCalendarStorage(key))
    credentials.refresh(build_http())

    return settings


@app.errorhandler(500)
def server_error(e):
    """Logs the stack trace for server errors."""

    timestamp = int(time())
    message = "Internal Server Error @ %d" % timestamp
    exception(message)

    return message, 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
