from flask import Flask
from flask import redirect
from flask import send_file
from logging import exception
from time import time

from artwork import Artwork
from auth import user_auth
from city import City
from commute import Commute
from google_calendar import GoogleCalendar
from response import epd_response
from response import png_response
from response import text_response
from schedule import Schedule

# The URL of the Medium story about Accent.
REDIRECT_URL = "https://medium.com/@maxbraun/meet-accent-352cfa95813a"

app = Flask(__name__)


@app.route("/artwork")
@user_auth(png_response)
def artwork(user=None):
    """Responds with a PNG version of the artwork image."""

    artwork = Artwork(user)
    image = artwork.image()
    return png_response(image)


@app.route("/city")
@user_auth(png_response)
def city(user=None):
    """Responds with a PNG version of the city image."""

    city = City(user)
    image = city.image()
    return png_response(image)


@app.route("/commute")
@user_auth(png_response)
def commute(user=None):
    """Responds with a PNG version of the commute image."""

    commute = Commute(user)
    image = commute.image()
    return png_response(image)


@app.route("/calendar")
@user_auth(png_response)
def calendar(user=None):
    """Responds with a PNG version of the calendar image."""

    calendar = GoogleCalendar(user)
    image = calendar.image()
    return png_response(image)


@app.route("/png")
@user_auth(png_response)
def png(user=None):
    """Responds with a PNG version of the scheduled image."""

    schedule = Schedule(user)
    image = schedule.image()
    return png_response(image)


@app.route("/epd")
@user_auth(epd_response)
def epd(user=None):
    """Responds with an e-paper display version of the scheduled image."""

    schedule = Schedule(user)
    image = schedule.image()
    return epd_response(image)


@app.route("/next")
@user_auth()
def next(user=None):
    """Responds with the milliseconds until the next image."""

    schedule = Schedule(user)
    milliseconds = schedule.delay()
    return text_response(str(milliseconds))


@app.route("/")
def root():
    """Redirects to the Medium story about Accent."""

    return redirect(REDIRECT_URL)


@app.route("/hello/<key>")
def hello(key):
    """Starts the new user flow."""

    return text_response("Not implemented yet")


@app.errorhandler(500)
def server_error(e):
    """Logs the stack trace for server errors."""

    timestamp = int(time())
    message = "Internal Server Error @ %d" % timestamp
    exception(message)

    return message, 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
