from google import genai
from google.genai.errors import APIError
from google.genai.types import GenerateImagesConfig
from google.genai.types import PersonGeneration
from google.genai.types import SafetyFilterLevel
from content import ContentError
from content import ImageContent
from io import BytesIO
from os import environ
from PIL import Image

# The prompt for generating images.
IMAGE_PROMPT = """
Eastern Christian Orthodox icon with artificial intelligence elements
"""

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
        self._client = genai.Client(
            vertexai=True,
            project=environ['GOOGLE_CLOUD_PROJECT'],
            location='us-central1')

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

        # Call the API to generate the image.
        try:
            response = self._client.models.generate_images(
                model='imagen-4.0-ultra-generate-preview-06-06',
                prompt=IMAGE_PROMPT,
                config=GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=config_aspect_ratio,
                    person_generation=PersonGeneration.ALLOW_ALL,
                    safety_filter_level=SafetyFilterLevel.BLOCK_ONLY_HIGH))
        except APIError as e:
            raise ContentError(f'Image generation failed: {e}')
        if not response.generated_images:
            raise ContentError('Empty image generation response')

        # Scale and crop the generated image.
        generated_image = response.generated_images[0]
        with BytesIO(generated_image.image.image_bytes) as image_data:
            with Image.open(image_data).convert('RGB') as image:
                # Scale to fill.
                scale = max(width / image.width, height / image.height)
                scaled_width = int(image.width * scale)
                scaled_height = int(image.height * scale)
                image = image.resize((scaled_width, scaled_height),
                                        resample=Image.LANCZOS)

                # Center crop.
                left = (scaled_width - width) // 2
                top = (scaled_height - height) // 2
                right = left + width
                bottom = top + height
                cropped_image = image.crop((left, top, right, bottom))

                return cropped_image
