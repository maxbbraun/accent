class ImageContent(object):
    """An abstract base class for image content."""

    def image(self, user, size):
        """Generates the current image for the specified user."""

        # Implemented in subclass.
        pass


class ContentError(Exception):
    """An error indicating issues generating content."""

    pass
