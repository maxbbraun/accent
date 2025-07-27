from google import genai
from google.genai.types import GenerateImagesConfig
from content import ContentError, ImageContent
from firestore import Firestore
from PIL import Image
from io import BytesIO
import logging

# The prompt for generating images.
IMAGE_PROMPT = 'Eastern Christian Orthodox icon but make it slightly AI'

# Supported aspect ratios for the image generation API.
ASPECT_RATIOS = [
    (1.0, '1:1'),
    (0.75, '3:4'),
    (4/3, '4:3'),
    (9/16, '9:16'),
    (16/9, '16:9'),
]

class AIcon(ImageContent):
    """AI-generated Eastern Christian Orthodox icons."""

    def __init__(self):
        self._firestore = Firestore()

    def image(self, user, width, height, variant):
        """Generates the AI icon image."""

        try:
            # Configure the API.
            api_key = self._firestore.gemini_api_key()
            client = genai.Client(api_key=api_key)

            # Find the aspect ratio that minimizes excess crop.
            def calculate_crop_ratio(ratio_tuple):
                target_ratio = width / height
                supported_ratio, _ = ratio_tuple
                if supported_ratio > target_ratio:
                    # Generated image is wider than target, crop sides
                    return supported_ratio / target_ratio
                else:
                    # Generated image is taller than target, crop top/bottom
                    return target_ratio / supported_ratio

            best_ratio_tuple = min(ASPECT_RATIOS, key=calculate_crop_ratio)
            config_aspect_ratio = best_ratio_tuple[1]

            # Generate the image using GenerateImagesConfig class
            config = GenerateImagesConfig(
                number_of_images=1,
                person_generation='allow_all',
                safety_filter_level='block_few',
                aspect_ratio=config_aspect_ratio,
            )

            response = client.models.generate_images(
                model='imagen-4.0-ultra-generate-preview-06-06',
                prompt=IMAGE_PROMPT,
                config=config
            )

            # Get the generated image
            if response.generated_images and len(response.generated_images) > 0:
                generated_image = response.generated_images[0]
                # Convert the image to PIL format
                image_bytes = generated_image.image.image_bytes
                image = Image.open(BytesIO(image_bytes)).convert('RGB')
            else:
                raise ContentError("No image generated from API response")

        except Exception as e:
            logging.error(f"Failed to generate AIcon: {e}")
            raise ContentError(f"Image generation failed: {e}")

        # Center crop the image to the requested dimensions
        # Scale to fill the target dimensions (crop excess)
        scale = max(width / image.width, height / image.height)
        scaled_width = int(image.width * scale)
        scaled_height = int(image.height * scale)
        image = image.resize((scaled_width, scaled_height), resample=Image.LANCZOS)

        # Calculate center crop coordinates
        left = (scaled_width - width) // 2
        top = (scaled_height - height) // 2
        right = left + width
        bottom = top + height

        # Crop from center to exact target dimensions
        cropped_image = image.crop((left, top, right, bottom))

        return cropped_image