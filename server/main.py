from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from googleapiclient.http import build_http
from logging import error
from logging import exception
from oauth2client.client import HttpAccessTokenRefreshError
from time import time

from artwork import Artwork
from auth import ACCOUNT_ACCESS_URL
from auth import google_calendar_step1
from auth import next_retry_response
from auth import oauth_step2
from auth import user_auth
from auth import validate_key
from city import City
from commute import Commute
from content import ContentError
from everyone import Everyone
from firestore import Firestore
from firestore import GoogleCalendarStorage
from geocoder import Geocoder
from google_calendar import GoogleCalendar
from response import content_response
from response import epd_response
from response import gif_response
from response import settings_url
from response import text_response
from schedule import Schedule

# The URL of the Medium story about Accent.
INFO_URL = ('https://medium.com/@maxbraun/meet-accent-352cfa95813a'
            '?source=friends_link&sk=4a0cab13290cf52ee5fb9c92d3e766aa')

# The URL of the Medium story explaining how to set up Accent.
SETUP_URL = 'https://medium.com/@maxbraun/setting-up-accent-b71a07c33ca9'

# The URL of the GitHub page with Accent's source code.
CODE_URL = 'https://github.com/maxbbraun/accent'

# The URL of the Accent Twitter profile.
SOCIAL_URL = 'https://twitter.com/AccentInk'

# The template for editing user data.
HELLO_TEMPLATE = 'hello.html'

# A geocoder instance with a shared cache.
geocoder = Geocoder()

# Helper library instances.
artwork = Artwork()
calendar = GoogleCalendar(geocoder)
city = City(geocoder)
commute = Commute(geocoder)
everyone = Everyone(geocoder)
schedule = Schedule(geocoder)

# The Flask app handling requests.
app = Flask(__name__)


@app.route('/artwork')
@user_auth(image_response=gif_response)
def artwork_gif(key=None, user=None, size=None):
    """Responds with a GIF version of the artwork image."""

    return content_response(artwork, gif_response, user, size)


@app.route('/city')
@user_auth(image_response=gif_response)
def city_gif(key=None, user=None, size=None):
    """Responds with a GIF version of the city image."""

    return content_response(city, gif_response, user, size)


@app.route('/commute')
@user_auth(image_response=gif_response)
def commute_gif(key=None, user=None, size=None):
    """Responds with a GIF version of the commute image."""
    return content_response(commute, gif_response, user, size)


@app.route('/calendar')
@user_auth(image_response=gif_response)
def calendar_gif(key=None, user=None, size=None):
    """Responds with a GIF version of the calendar image."""

    return content_response(calendar, gif_response, user, size)


@app.route('/everyone')
@user_auth(image_response=gif_response)
def everyone_gif(key=None, user=None, size=None):
    """Responds with a GIF version of the everyone image."""

    return content_response(everyone, gif_response, user, size)


@app.route('/gif')
@user_auth(image_response=gif_response)
def gif(key=None, user=None, size=None):
    """Responds with a GIF version of the scheduled image."""

    return content_response(schedule, gif_response, user, size)


@app.route('/epd')
@user_auth(image_response=epd_response)
def epd(key=None, user=None, size=None):
    """Responds with an e-paper display version of the scheduled image."""

    return content_response(schedule, epd_response, user, size)


@app.route('/next')
@user_auth(bad_response=next_retry_response)
def next(key=None, user=None, size=None):
    """Responds with the milliseconds until the next image."""

    try:
        milliseconds = schedule.delay(user)
        return text_response(str(milliseconds))
    except ContentError as e:
        exception('Failed to create next content: %s' % e)
        return next_retry_response()


@app.route('/')
@app.route('/info')
def info():
    """Redirects to the Medium story about Accent."""

    return redirect(INFO_URL)


@app.route('/setup')
def setup():
    """Redirects to the Medium story explaining how to set up Accent."""

    return redirect(SETUP_URL)


@app.route('/code')
def code():
    """Redirects to the GitHub page with Accent's source code."""

    return redirect(CODE_URL)


@app.route('/social')
def social():
    """Redirects to the Accent Twitter profile."""

    return redirect(SOCIAL_URL)


@app.route('/hello/<key>', methods=['GET'])
@validate_key
def hello_get(key):
    """Responds with a form for editing user data."""

    # Look up any existing user data.
    calendar_storage = GoogleCalendarStorage(key)
    calendar_credentials = calendar_storage.get()

    # Force a Google Calendar credentials refresh to get the latest status.
    if calendar_credentials:
        try:
            calendar_credentials.refresh(build_http())
        except HttpAccessTokenRefreshError as e:
            error('Calendar token refresh error: %s' % e)
            calendar_storage.delete()
            calendar_credentials = None

    calendar_connected = calendar_credentials is not None
    return render_template(HELLO_TEMPLATE, key=key, user=Firestore().user(key),
                           calendar_connected=calendar_connected,
                           calendar_connect_url=google_calendar_step1(key),
                           calendar_disconnect_url=ACCOUNT_ACCESS_URL)


@app.route('/hello/<key>', methods=['POST'])
@validate_key
def hello_post(key):
    """Saves user data and responds with the updated form."""

    # Build the schedule from the form data, dropping any empty entries.
    form = request.form
    list_form = form.to_dict(flat=False)
    schedule_form = zip(list_form['schedule_name'],
                        list_form['schedule_start'],
                        list_form['schedule_image'])
    schedule = [{'name': name, 'start': start, 'image': image}
                for name, start, image in schedule_form
                if name and start and image]

    # Update the existing user data or create a new one.
    firestore = Firestore()
    firestore.set_user(key, {
        'home': form['home'],
        'work': form['work'],
        'travel_mode': form['travel_mode'],
        'schedule': schedule})

    # Redirect back to the GET version.
    return redirect(settings_url(key))


@app.route('/oauth')
def oauth():
    """Handles any OAuth flow redirects."""

    # Always redirect back to the settings page.
    key = request.args.get('state')
    settings = redirect(settings_url(key))

    # Handle any errors, notably the user declining.
    oauth_error = request.args.get('error')
    if oauth_error:
        error('OAuth error: %s' % oauth_error)
        return settings

    # Continue the flow based on the scope.
    scope = request.args.get('scope')
    code = request.args.get('code')
    oauth_step2(key, scope, code)

    return settings


@app.errorhandler(500)
def server_error(e):
    """Logs the stack trace for server errors."""

    timestamp = int(time())
    message = 'Internal Server Error @ %d' % timestamp
    exception(message)

    return message, 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
