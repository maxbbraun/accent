import math
from os.path import join as path_join
from PIL import Image
from random import random

from content import ContentError
from content import ImageContent
from firestore import DataError
from local_time import LocalTime
from sun import Sun
from weather import Weather

# The directory containing city image assets.
ASSETS_DIR = 'assets/city'


class City(ImageContent):
    """A dynamic city scene that changes with the weather and other factors."""

    def __init__(self, geocoder):
        self._local_time = LocalTime(geocoder)
        self._sun = Sun(geocoder)
        self._weather = Weather(geocoder)

    def _day_of_year(self, user):
        """Returns the current day of the year in the users's time zone."""

        return self._local_time.now(user).timetuple().tm_yday

    def _modulo_3_0(self, user):
        """Returns True if the current day of the year modulo 3 is 0."""

        return self._day_of_year(user) % 3 == 0

    def _modulo_3_1(self, user):
        """Returns True if the current day of the year modulo 3 is 1."""

        return self._day_of_year(user) % 3 == 1

    def _modulo_3_2(self, user):
        """Returns True if the current day of the year modulo 3 is 2."""

        return self._day_of_year(user) % 3 == 2

    def _layers(self):
        """The list of layers making up the city scene. Each layer is a
        dictionary with a combination of the following keys.

        Exactly one of...
             'condition': A function that needs to evaluate to True for this
                          layer to be drawn.
         'not_condition': A function that needs to evaluate to False for this
                          layer to be drawn.
         'and_condition': A list of functions that all have to evaluate to True
                          for this layer to be drawn.
          'or_condition': A list of functions where at least one has to
                          evaluate to True for this layer to be drawn.
        'else_condition': A list of file paths (identifying layers) that have
                          to not have been drawn for this layer to be drawn.

        And optionally...
           'probability': The probability in percent for this layer to be
                          drawn.

        Either a layer group...
                'layers': A list of layer dictionaries to be drawn recursively.

        Or layer content...
                  'file': The path of the image file for this layer relative to
                          ASSETS_DIR.

        With a fixed position...
                    'xy': A tuple defining the top left corner of this layer.

        Or a dynamic position...
          'xy_transform': A function that evaluates to a tuple defining the top
                          left corner of this layer.
               'xy_data': The argument passed to the function specified in
                          'xy_transform'.
        """

        return [{
            'condition': self._sun.is_daylight,
            'layers': [
                {
                    'file': 'day/environment/water-day.gif',
                    'xy': (0, 0),
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/environment/water-flat-day.gif',
                    'xy': (0, 0),
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/environment/isle-day.gif',
                    'xy': (0, 0)
                },
                {
                    'file': 'day/blocks/bldg-facstdo-day.gif',
                    'xy': (262, 9)
                },
                {
                    'file': 'day/misc/lightpole-day.gif',
                    'xy': (130, 5)
                },
                {
                    'file': 'day/blocks/bldg-verylittlegravitas-day.gif',
                    'xy': (188, 18)
                },
                {
                    'file': 'day/blocks/block-D-day.gif',
                    'xy': (74, 59)
                },
                {
                    'file': 'day/vehicles/van2-247-yp-day.gif',
                    'xy': (156, 116),
                    'probability': 50
                },
                {
                    'file': 'day/misc/streetlight-xp-day.gif',
                    'xy': (314, 11)
                },
                {
                    'file': 'day/blocks/block-F-day.gif',
                    'xy': (418, 6)
                },
                {
                    'file': 'day/blocks/bldg-home-day.gif',
                    'xy': (422, 36)
                },
                {
                    'file': 'day/vehicles/boat3-yp-day.gif',
                    'xy': (590, 87),
                    'probability': 50
                },
                {
                    'file': ('day/characters/blockbob/'
                             'blockbob-driving-xp-day.gif'),
                    'xy': (418, 109),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': ('day/characters/blockbob/'
                             'blockbob-driving-xp-day-rain.gif'),
                    'xy': (418, 93),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/blocks/bldg-robosuper-day.gif',
                    'xy': (540, 116)
                },
                {
                    'file': 'day/blocks/block-A/block-A-day.gif',
                    'xy': (200, 6),
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/blocks/block-A/block-A-day-rain.gif',
                    'xy': (200, 6),
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/characters/blockbob/blockbob-sitting-day.gif',
                    'xy': (276, 78),
                    'else_condition': [
                        'day/characters/blockbob/blockbob-driving-xp-day.gif',
                        ('day/characters/blockbob/'
                         'blockbob-driving-xp-day-rain.gif')
                    ],
                },
                {
                    'file': ('day/misc/computersays/'
                             'billboard-computer-no-day.gif'),
                    'xy': (386, 51),
                    'probability': 50
                },
                {
                    'file': ('day/misc/computersays/'
                             'billboard-computer-yes-day.gif'),
                    'xy': (386, 51),
                    'else_condition': [
                        'day/misc/computersays/billboard-computer-no-day.gif'
                    ]
                },
                {
                    'file': 'day/misc/3letterLED/3letterLED-UFO-day.gif',
                    'xy': (354, 125),
                    'condition': self._modulo_3_0
                },
                {
                    'file': 'day/misc/3letterLED/3letterLED-LOL-day.gif',
                    'xy': (354, 125),
                    'condition': self._modulo_3_1
                },
                {
                    'file': 'day/misc/3letterLED/3letterLED-404-day.gif',
                    'xy': (354, 125),
                    'condition': self._modulo_3_2
                },
                {
                    'file': 'day/misc/streetlight-yp-day.gif',
                    'xy': (168, 125)
                },
                {
                    'file': 'day/characters/robogroup/robogroup-day.gif',
                    'xy': (554, 168),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/characters/robogroup/robogroup-day-rain.gif',
                    'xy': (547, 157),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/misc/streetlight-xm-day.gif',
                    'xy': (596, 164)
                },
                {
                    'file': 'day/misc/streetlight-yp-day.gif',
                    'xy': (516, 119)
                },
                {
                    'file': ('day/characters/deliverybiker/'
                             'deliverybiker-xm-day.gif'),
                    'xy': (500, 142),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': ('day/characters/deliverybiker/'
                             'deliverybiker-xm-day-rain.gif'),
                    'xy': (492, 135),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/blocks/block-E/block-E-day.gif',
                    'xy': (12, 51),
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/blocks/block-E/block-E-day-rain.gif',
                    'xy': (12, 51),
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/vehicles/boat1/boat1-yp-day.gif',
                    'xy': (6, 238),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/vehicles/boat1/boat1-yp-day-rain.gif',
                    'xy': (6, 216),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/misc/bench-day.gif',
                    'xy': (48, 245)
                },
                {
                    'file': 'day/vehicles/boat2-ym-day.gif',
                    'xy': (12, 261),
                    'probability': 50
                },
                {
                    'file': 'day/characters/ladybiker/ladybiker-day.gif',
                    'xy': (102, 251),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/characters/ladybiker/ladybiker-day-rain.gif',
                    'xy': (102, 234),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/misc/streetlight-ym-day.gif',
                    'xy': (38, 224)
                },
                {
                    'file': 'day/vehicles/van1-yp-day.gif',
                    'xy': (412, 164),
                    'probability': 50
                },
                {
                    'file': 'day/vehicles/van2-milk-yp-day.gif',
                    'xy': (440, 158),
                    'probability': 50
                },
                {
                    'file': 'day/vehicles/van2-yp-day.gif',
                    'xy': (388, 184),
                    'probability': 50
                },
                {
                    'file': 'day/vehicles/car2-xp-day.gif',
                    'xy': (236, 213),
                    'probability': 50
                },
                {
                    'file': 'day/vehicles/car1-yp-day.gif',
                    'xy': (152, 266),
                    'probability': 50
                },
                {
                    'file': 'day/blocks/block-B-day.gif',
                    'xy': (334, 191)
                },
                {
                    'file': 'day/misc/cleat-x-day.gif',
                    'xy': (518, 285)
                },
                {
                    'file': ('day/characters/robogroup/'
                             'robogroup-barge-empty-xm-day.gif'),
                    'xy': (574, 222),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': ('day/characters/robogroup/'
                             'robogroup-barge-empty-xm-day-rain.gif'),
                    'xy': (574, 218),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/blocks/bldg-jetty-day.gif',
                    'xy': (516, 230)
                },
                {
                    'file': 'day/misc/streetlight-yp-day.gif',
                    'xy': (528, 255)
                },
                {
                    'file': 'day/blocks/park-day.gif',
                    'xy': (379, 252)
                },
                {
                    'file': 'day/characters/dogcouple-day.gif',
                    'xy': (509, 312),
                    'probability': 50
                },
                {
                    'file': 'day/characters/girl/girlwbird-day.gif',
                    'xy': (400, 315),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/characters/girl/girlwbird-day-rain.gif',
                    'xy': (404, 303),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/misc/streetlight-ym-day.gif',
                    'xy': (294, 218)
                },
                {
                    'file': 'day/blocks/block-C-day.gif',
                    'xy': (216, 197)
                },
                {
                    'file': 'day/misc/cleat-y-day.gif',
                    'xy': (400, 346)
                },
                {
                    'file': 'day/characters/vrguys/vrguy-A-day.gif',
                    'xy': (217, 298),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/characters/vrguys/vrguy-A-day-rain.gif',
                    'xy': (203, 276),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/characters/vrguys/vrguy-B-day.gif',
                    'xy': (240, 305),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'day/characters/vrguys/vrguy-B-day-rain.gif',
                    'xy': (234, 293),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/blocks/bldg-honeybucket-day.gif',
                    'xy': (146, 291)
                },
                {
                    'file': 'day/misc/memorial-minicyclops-day.gif',
                    'xy': (40, 291)
                },
                {
                    'file': 'day/misc/cleat-y-day.gif',
                    'xy': (10, 309)
                },
                {
                    'file': 'day/misc/cleat-y-day.gif',
                    'xy': (26, 317)
                },
                {
                    'file': 'day/misc/memorial-cyclops-day.gif',
                    'xy': (62, 289)
                },
                {
                    'file': 'day/vehicles/yacht2-xm-day.gif',
                    'xy': (544, 302),
                    'probability': 50
                },
                {
                    'file': 'day/vehicles/yacht1-xm-day.gif',
                    'xy': (506, 334),
                    'probability': 50
                },
                {
                    'file': 'day/vehicles/houseboat/houseboat-day.gif',
                    'xy': (163, 326),
                    'probability': 50
                },
                {
                    'file': 'day/misc/streetlight-xp-day.gif',
                    'xy': (216, 322)
                },
                {
                    'file': 'day/environment/sun-day.gif',
                    'xy': (19, 17)
                },
                {
                    'file': 'day/environment/rain1-day.gif',
                    'xy': (0, 0),
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'day/environment/cloud1-day.gif',
                    'xy': (523, 5),
                    'or_condition': [self._weather.is_partly_cloudy,
                                     self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud2-day.gif',
                    'xy': (-43, 41),
                    'or_condition': [self._weather.is_partly_cloudy,
                                     self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud2-day.gif',
                    'xy': (519, 177),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud3-day.gif',
                    'xy': (49, 96),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud4-day.gif',
                    'xy': (195, 156),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud5-day.gif',
                    'xy': (339, 70),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud6-day.gif',
                    'xy': (93, 264),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud7-day.gif',
                    'xy': (472, 247),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'day/environment/cloud8-day.gif',
                    'xy': (-18, 314),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                }
            ]
        }, {
            'not_condition': self._sun.is_daylight,
            'layers': [
                {
                    'file': 'night/environment/water-night.gif',
                    'xy': (0, 0),
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'night/environment/water-flat-night.gif',
                    'xy': (0, 0),
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'night/environment/isle-night.gif',
                    'xy': (0, 0)
                },
                {
                    'file': 'night/blocks/bldg-facstdo-night.gif',
                    'xy': (262, 9)
                },
                {
                    'file': 'night/misc/lightpole-night.gif',
                    'xy': (130, 5)
                },
                {
                    'file': 'night/blocks/bldg-verylittlegravitas-night.gif',
                    'xy': (188, 18)
                },
                {
                    'file': 'night/blocks/block-D-night.gif',
                    'xy': (74, 59)
                },
                {
                    'file': 'night/vehicles/van2-247-yp-night.gif',
                    'xy': (142, 116),
                    'probability': 50
                },
                {
                    'file': 'night/misc/streetlight-xp-night.gif',
                    'xy': (314, 11)
                },
                {
                    'file': 'night/blocks/block-F-night.gif',
                    'xy': (418, 6)
                },
                {
                    'file': 'night/blocks/bldg-home-night.gif',
                    'xy': (422, 36)
                },
                {
                    'file': 'night/vehicles/boat3-yp-night.gif',
                    'xy': (590, 87),
                    'probability': 80
                },
                {
                    'file': ('night/characters/blockbob/'
                             'blockbob-driving-xp-night.gif'),
                    'xy': (418, 109),
                    'probability': 50,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': ('night/characters/blockbob/'
                             'blockbob-driving-xp-night-rain.gif'),
                    'xy': (418, 93),
                    'probability': 50,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'night/blocks/bldg-robosuper-night.gif',
                    'xy': (540, 116)
                },
                {
                    'file': 'night/characters/dogcouple-night.gif',
                    'xy': (578, 175)
                },
                {
                    'file': 'night/vehicles/car3-yp-night.gif',
                    'xy': (532, 186),
                    'probability': 50
                },
                {
                    'file': 'night/blocks/block-A/block-A-night.gif',
                    'xy': (200, 6),
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'night/blocks/block-A/block-A-night-rain.gif',
                    'xy': (200, 6),
                    'condition': self._weather.is_rainy
                },
                {
                    'file': ('night/characters/blockbob/'
                             'blockbob-sitting-night.gif'),
                    'xy': (276, 78),
                    'else_condition': [
                        ('night/characters/blockbob/'
                         'blockbob-driving-xp-night.gif'),
                        ('night/characters/blockbob/'
                         'blockbob-driving-xp-night-rain.gif')
                    ]
                },
                {
                    'file': ('night/misc/computersays/'
                             'billboard-computer-no-night.gif'),
                    'xy': (386, 51),
                    'probability': 50
                },
                {
                    'file': ('night/misc/computersays/'
                             'billboard-computer-yes-night.gif'),
                    'xy': (386, 51),
                    'else_condition': [
                        ('night/misc/computersays/'
                         'billboard-computer-no-night.gif')
                    ]
                },
                {
                    'file': 'night/misc/3letterLED/3letterLED-UFO-night.gif',
                    'xy': (354, 125),
                    'condition': self._modulo_3_0
                },
                {
                    'file': 'night/misc/3letterLED/3letterLED-LOL-night.gif',
                    'xy': (354, 125),
                    'condition': self._modulo_3_1
                },
                {
                    'file': 'night/misc/3letterLED/3letterLED-404-night.gif',
                    'xy': (354, 125),
                    'condition': self._modulo_3_2
                },
                {
                    'file': 'night/misc/streetlight-yp-night.gif',
                    'xy': (168, 125)
                },
                {
                    'file': 'night/misc/streetlight-xm-night.gif',
                    'xy': (596, 164)
                },
                {
                    'file': 'night/misc/streetlight-yp-night.gif',
                    'xy': (516, 119)
                },
                {
                    'file': 'night/blocks/block-E-night.gif',
                    'xy': (12, 51)
                },
                {
                    'file': 'night/vehicles/boat1-yp-night.gif',
                    'xy': (6, 238),
                    'probability': 80,
                    'not_condition': self._weather.is_rainy
                },
                {
                    'file': 'night/vehicles/boat1-yp-night-rain.gif',
                    'xy': (6, 216),
                    'probability': 80,
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'night/misc/bench-night.gif',
                    'xy': (48, 245)
                },
                {
                    'file': 'night/vehicles/boat2-ym-night.gif',
                    'xy': (12, 261),
                    'probability': 80
                },
                {
                    'file': 'night/misc/streetlight-ym-night.gif',
                    'xy': (38, 224)
                },
                {
                    'file': 'night/vehicles/van1-yp-night.gif',
                    'xy': (400, 164),
                    'probability': 50
                },
                {
                    'file': 'night/vehicles/van2-milk-yp-night.gif',
                    'xy': (440, 158),
                    'probability': 50
                },
                {
                    'file': 'night/vehicles/van2-yp-night.gif',
                    'xy': (374, 184),
                    'probability': 50
                },
                {
                    'file': 'night/vehicles/car2-xp-night.gif',
                    'xy': (236, 213),
                    'probability': 50
                },
                {
                    'file': 'night/vehicles/car1-yp-night.gif',
                    'xy': (138, 266),
                    'probability': 50
                },
                {
                    'file': 'night/blocks/block-B-night.gif',
                    'xy': (334, 191)
                },
                {
                    'file': 'night/misc/cleat-x-night.gif',
                    'xy': (518, 285)
                },
                {
                    'file': ('night/characters/robogroup/'
                             'robogroup-barge-xm-night.gif'),
                    'xy': (574, 222),
                    'probability': 50
                },
                {
                    'file': 'night/blocks/bldg-jetty-night.gif',
                    'xy': (516, 230)
                },
                {
                    'file': 'night/misc/streetlight-yp-night.gif',
                    'xy': (528, 255)
                },
                {
                    'file': 'night/blocks/park-night.gif',
                    'xy': (379, 252)
                },
                {
                    'file': 'night/misc/streetlight-ym-night.gif',
                    'xy': (294, 218)
                },
                {
                    'file': 'night/blocks/block-C-night.gif',
                    'xy': (216, 197)
                },
                {
                    'file': 'night/misc/cleat-y-night.gif',
                    'xy': (400, 346)
                },
                {
                    'file': 'night/blocks/bldg-honeybucket-night.gif',
                    'xy': (146, 291)
                },
                {
                    'file': 'night/misc/memorial-minicyclops-night.gif',
                    'xy': (40, 291)
                },
                {
                    'file': 'night/misc/cleat-y-night.gif',
                    'xy': (10, 309)
                },
                {
                    'file': 'night/misc/cleat-y-night.gif',
                    'xy': (26, 317)
                },
                {
                    'file': 'night/misc/memorial-cyclops-night.gif',
                    'xy': (62, 289)
                },
                {
                    'file': 'night/vehicles/yacht2-xm-night.gif',
                    'xy': (544, 302),
                    'probability': 80
                },
                {
                    'file': 'night/vehicles/yacht1-xm-night.gif',
                    'xy': (506, 334),
                    'probability': 80
                },
                {
                    'file': 'night/vehicles/houseboat/houseboat-night.gif',
                    'xy': (163, 326),
                    'probability': 80
                },
                {
                    'file': 'night/misc/streetlight-xp-night.gif',
                    'xy': (216, 322)
                },
                {
                    'file': 'night/environment/moon-night.gif',
                    'xy': (19, 17)
                },
                {
                    'file': 'night/environment/rain1-night.gif',
                    'xy': (0, 0),
                    'condition': self._weather.is_rainy
                },
                {
                    'file': 'night/environment/cloud1-night.gif',
                    'xy': (523, 5),
                    'or_condition': [self._weather.is_partly_cloudy,
                                     self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud2-night.gif',
                    'xy': (-43, 41),
                    'or_condition': [self._weather.is_partly_cloudy,
                                     self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud2-night.gif',
                    'xy': (519, 177),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud3-night.gif',
                    'xy': (49, 96),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud4-night.gif',
                    'xy': (195, 156),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud5-night.gif',
                    'xy': (339, 70),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud6-night.gif',
                    'xy': (93, 264),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud7-night.gif',
                    'xy': (472, 247),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                },
                {
                    'file': 'night/environment/cloud8-night.gif',
                    'xy': (-18, 314),
                    'or_condition': [self._weather.is_cloudy,
                                     self._weather.is_rainy]
                }
            ]
        }]

    def _draw_layers(self, image, layers, user, offset):
        """Draws a list of layers onto an image."""

        # Keep track of drawn layers.
        drawn_files = []

        # Draw the layers in order.
        for layer in layers:
            try:
                # Simple condition has to be true.
                if not layer['condition'](user):
                    continue
            except KeyError:
                pass

            try:
                # Negated condition has to be false.
                if layer['not_condition'](user):
                    continue
            except KeyError:
                pass

            try:
                # All and-conditions have to be true.
                if not all([c(user) for c in layer['and_condition']]):
                    continue
            except KeyError:
                pass

            try:
                # One or-condition has to be true.
                if not any([c(user) for c in layer['or_condition']]):
                    continue
            except KeyError:
                pass

            try:
                # Else layers have to not have been drawn.
                if not set(layer['else_condition']).isdisjoint(drawn_files):
                    continue
            except KeyError:
                pass

            try:
                # Evaluate a random probability.
                if layer['probability'] <= 100 * random():
                    continue
            except KeyError:
                pass

            # Recursively draw groups of layers.
            try:
                self._draw_layers(image, layer['layers'], user, offset)
                continue  # Don't try to draw layer groups.
            except KeyError:
                pass

            # Get the coordinates, optionally transforming them first.
            try:
                x, y = layer['xy_transform'](layer['xy_data'])
            except KeyError:
                x, y = layer['xy']
            
            # Draw the layer.
            path = path_join(ASSETS_DIR, layer['file'])
            bitmap = Image.open(path).convert('RGBA')
            image.paste(bitmap, (x + offset[0], y + offset[1]), bitmap)

            # Remember the drawn file for the else condition.
            drawn_files.append(layer['file'])

    def image(self, user, size):
        """Generates the current city image."""

        background_color = (0,0,0)
        if self._sun.is_daylight(user):
            background_color = (255,255,255)

        image = Image.new(mode='RGB', size=size, color=background_color)
        try:
            offset = (
                math.floor((size[0] - 640) / 2), 
                math.floor((size[1] - 384) / 2)
            )
            self._draw_layers(image, self._layers(), user, offset)
            return image
        except DataError as e:
            raise ContentError(e)
