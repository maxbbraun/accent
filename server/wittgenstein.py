from content import ContentError
from io import BytesIO
from requests import get
from requests.exceptions import RequestException
from PIL import Image

from content import ImageContent

# The URL for requesting a random Wittgenstein 2022 proposition.
RANDOM_PROPOSITION_URL = 'https://wittgenstein.app/random.json'

# The URL of the Wittgenstein 2022 preview image for a given proposition ID.
PREVIEW_IMAGE_URL = 'https://wittgenstein.app/preview/%s.png'


class Wittgenstein(ImageContent):
    """A random proposition from Wittgenstein 2022."""

    def image(self, _, width, height):
        """Picks a random proposition preview image."""

        try:
            # Request a random proposition.
            json = get(RANDOM_PROPOSITION_URL).json()
            id = json['id']

            # Download the preview image for the proposition.
            image_data = BytesIO(get(PREVIEW_IMAGE_URL % id).content)
            image = Image.open(image_data).convert('RGB')
        except (RequestException, KeyError) as e:
            raise ContentError(e)

        # Resize the image and extend the background.
        scale = min(width / image.width, height / image.height)
        scaled_width = int(image.width * scale)
        scaled_height = int(image.height * scale)
        image = image.resize((scaled_width, scaled_height),
                             resample=Image.LANCZOS)
        canvas = Image.new(mode='RGB', size=(width, height), color='white')
        x = (width - scaled_width) // 2
        y = (height - scaled_height) // 2
        canvas.paste(image, (x, y), 0)

        return canvas
