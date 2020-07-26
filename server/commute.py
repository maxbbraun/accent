from content import ContentError
from firestore import DataError
from google_maps import GoogleMaps
from graphics import draw_text
from graphics import SUBVARIO_CONDENSED_MEDIUM
from content import ImageContent

# The color of the directions text.
DIRECTIONS_TEXT_COLOR = (255, 255, 255)

# The color of the box behind the directions text.
DIRECTIONS_BOX_COLOR = (0, 0, 0)

# The color of the border around the directions text.
DIRECTIONS_BORDER_COLOR = (255, 255, 255)

# The width of the border around the directions text.
DIRECTIONS_BORDER_WIDTH = 3

# The padding of the box around the directions text.
DIRECTIONS_BOX_PADDING = 8


class Commute(ImageContent):
    """The commute route on a map."""

    def __init__(self, geocoder):
        self._google_maps = GoogleMaps(geocoder)

    def image(self, user, size):
        """Generates the current commute image."""

        # Extract the directions data.
        try:
            directions = self._google_maps.directions(user)
            status = directions['status']
            if status != 'OK':
                try:
                    error_message = directions['error_message']
                    raise DataError(error_message)
                except KeyError:
                    raise DataError(status)
            routes = directions['routes']
            route = routes[0]
            polyline = route['overview_polyline']['points']
            summary = route['summary']
            leg = route['legs'][0]  # Expect one leg.
            try:
                duration = leg['duration_in_traffic']['text']
            except KeyError:
                duration = leg['duration']['text']
        except (DataError, IndexError, KeyError) as e:
            raise ContentError(e)
        # Get the static map with the route as an image.
        try:
            image = self._google_maps.map_image(
                polyline=polyline, 
                size=size)
        except DataError as e:
            raise ContentError(e)

        # Draw the directions text inside a centered box.
        if summary:
            directions_text = '%s via %s' % (duration, summary)
        else:
            directions_text = duration
        draw_text(directions_text,
                  font_spec=SUBVARIO_CONDENSED_MEDIUM,
                  text_color=DIRECTIONS_TEXT_COLOR,
                  anchor='center',
                  box_color=DIRECTIONS_BOX_COLOR,
                  box_padding=DIRECTIONS_BOX_PADDING,
                  border_color=DIRECTIONS_BORDER_COLOR,
                  border_width=DIRECTIONS_BORDER_WIDTH,
                  image=image)

        return image
