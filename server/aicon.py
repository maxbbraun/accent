import base64
import binascii
from google import auth
from io import BytesIO
from os import environ
from PIL import Image
import requests

from content import ContentError
from content import ImageContent
from epd import ensure_rgb

# The prompt for generating images.
IMAGE_PROMPT = """
Eastern Christian Orthodox icon with artificial intelligence elements
"""

# The model to use for image generation.
IMAGE_MODEL = 'imagen-4.0-ultra-generate-001'

# The scope for authenticating with the Google Cloud Vertex AI API.
AUTH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'

# The location for the Google Cloud Vertex AI API.
LOCATION = 'us-central1'

# Supported aspect ratios for the image generation API.
ASPECT_RATIOS = [
    (1.0, '1:1'),
    (0.75, '3:4'),
    (4/3, '4:3'),
    (9/16, '9:16'),
    (16/9, '16:9')]

class AIcon(ImageContent):
    """AI-themed icons."""

    def __init__(self):
        # Configure the API.
        self._project = environ['GOOGLE_CLOUD_PROJECT']
        self._location = LOCATION
        self._model = IMAGE_MODEL
        self._credentials, _ = auth.default(scopes=[AUTH_SCOPE])

    def _access_token(self):
        """Gets a fresh access token for API calls."""

        # Refresh the credentials, if needed.
        if not self._credentials.valid:
            try:
                self._credentials.refresh(auth.transport.requests.Request())
            except auth.exceptions.RefreshError as e:
                raise ContentError(f'Failed to refresh credentials: {e}')

        # Return the access token.
        return self._credentials.token

    def image(self, user, width, height, variant):
        """Generates the AI icon image."""

        # Find the aspect ratio that minimizes excess crop.
        def calculate_crop_ratio(ratio_tuple):
            target_ratio = width / height
            supported_ratio, _ = ratio_tuple
            if supported_ratio > target_ratio:
                # Generated image is wider than target, crop sides.
                return supported_ratio / target_ratio
            else:
                # Generated image is taller than target, crop top/bottom.
                return target_ratio / supported_ratio
        best_ratio_tuple = min(ASPECT_RATIOS, key=calculate_crop_ratio)
        config_aspect_ratio = best_ratio_tuple[1]

        # Request a generated image from the Google Cloud Vertex AI API.
        url = (
            f'https://{self._location}-aiplatform.googleapis.com/v1/'
            f'projects/{self._project}/locations/{self._location}/'
            f'publishers/google/models/{self._model}:predict')
        headers = {
            'Authorization': f'Bearer {self._access_token()}',
            'Content-Type': 'application/json'}
        payload = {
            'instances': [{'prompt': IMAGE_PROMPT}],
            'parameters': {
                'sampleCount': 1,
                'aspectRatio': config_aspect_ratio,
                'personGeneration': 'allow_all',
                'safetyFilterLevel': 'block_only_high'}}
        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ContentError(f'Image generation API request failed: {e}')

        # Extract the Base64 image data from the response.
        try:
            result = response.json()
            prediction = result['predictions'][0]
            image_base64 = prediction['bytesBase64Encoded']
            image_bytes = base64.b64decode(image_base64)
        except (IndexError, KeyError, TypeError) as e:
            raise ContentError(f'Invalid API response: {e}')
        except (requests.JSONDecodeError, binascii.Error) as e:
            raise ContentError(f'Invalid API response content: {e}')

        # Scale and crop the generated image.
        with BytesIO(image_bytes) as image_data:
            with ensure_rgb(Image.open(image_data)) as image:

                # Scale to fill.
                scale = max(width / image.width, height / image.height)
                scaled_width = int(image.width * scale)
                scaled_height = int(image.height * scale)
                with image.resize((scaled_width, scaled_height),
                                  resample=Image.LANCZOS) as scaled_image:

                    # Center crop.
                    left = (scaled_width - width) // 2
                    top = (scaled_height - height) // 2
                    right = left + width
                    bottom = top + height
                    with scaled_image.crop((left, top, right, bottom)) as cropped_image:
                        return cropped_image
