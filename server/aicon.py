from google import genai
from google.genai.types import GenerateImagesConfig
from content import ContentError, ImageContent
from firestore import Firestore
from PIL import Image
from io import BytesIO
import logging

# The prompt for generating images.
IMAGE_PROMPT = "Eastern Christian Orthodox icon but make it slightly AI"

class AIcon(ImageContent):
    """AI-generated Eastern Christian Orthodox icons using Imagen 4 Ultra."""

    def __init__(self):
        self._firestore = Firestore()

    def image(self, user, width, height, variant):
        """Generates the icon image"""

        try:
            # Configure the API
            api_key = self._firestore.gemini_api_key()
            client = genai.Client(api_key=api_key)

            # Calculate the appropriate aspect ratio based on requested dimensions
            aspect_ratio = width / height
            
            # Map to closest supported aspect ratio options for Imagen 4 Ultra
            # Available options: 1:1, 3:4, 4:3, 9:16, 16:9
            if abs(aspect_ratio - 1.0) < 0.1:  # Square (1:1)
                config_aspect_ratio = "1:1"
            elif abs(aspect_ratio - 0.75) < 0.1:  # Portrait 3:4
                config_aspect_ratio = "3:4"
            elif abs(aspect_ratio - 1.33) < 0.1:  # Landscape 4:3
                config_aspect_ratio = "4:3"
            elif abs(aspect_ratio - 0.56) < 0.1:  # Portrait 9:16
                config_aspect_ratio = "9:16"
            elif abs(aspect_ratio - 1.78) < 0.1:  # Landscape 16:9
                config_aspect_ratio = "16:9"
            else:
                # Default to square if no close match
                config_aspect_ratio = "1:1"

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

        # Resize the image to fit the requested dimensions
        scale = min(width / image.width, height / image.height)
        scaled_width = int(image.width * scale)
        scaled_height = int(image.height * scale)
        image = image.resize((scaled_width, scaled_height), resample=Image.LANCZOS)

        # Create a canvas and center the image
        canvas = Image.new(mode='RGB', size=(width, height), color='white')
        x = (width - scaled_width) // 2
        y = (height - scaled_height) // 2
        canvas.paste(image, (x, y))

        return canvas