from content import ContentError
from io import BytesIO
from requests import get
from requests.exceptions import RequestException
from PIL import Image

from content import ImageContent
from epd import ensure_rgb

# The URL for requesting a random Wittgenstein 2022 proposition.
RANDOM_PROPOSITION_URL = 'https://wittgenstein.app/random.json'

# The URL of the Wittgenstein 2022 preview image for a given proposition ID.
PREVIEW_IMAGE_URL = 'https://wittgenstein.app/preview/%s.png'


class Wittgenstein(ImageContent):
    """A random proposition from Wittgenstein 2022."""

    def image(self, user, width, height, variant):
        """Picks a random proposition preview image."""

        try:
            # Request a random proposition.
            json = get(RANDOM_PROPOSITION_URL).json()
            id = json['id']

            # Download the preview image for the proposition.
            image_bytes = get(PREVIEW_IMAGE_URL % id).content
        except (RequestException, KeyError) as e:
            raise ContentError(e)

        # Resize the image and extend the background.
        with BytesIO(image_bytes) as image_data:
            with ensure_rgb(Image.open(image_data)) as image:
                # Scale to fit.
                scale = min(width / image.width, height / image.height)
                scaled_width = int(image.width * scale)
                scaled_height = int(image.height * scale)
                with image.resize(
                        (scaled_width, scaled_height),
                        resample=Image.Resampling.LANCZOS) as scaled_image:

                    # Extend the background.
                    with Image.new(mode='RGB', size=(width, height),
                                   color='white') as canvas:
                        x = (width - scaled_width) // 2
                        y = (height - scaled_height) // 2
                        canvas.paste(scaled_image, (x, y), 0)

                        return canvas
