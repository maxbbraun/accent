class ImageContent(object):
    """An abstract base class for image content."""

    def image(self, user, width, height):
        """Generates the current image for the specified user."""

        raise NotImplementedError('Missing image content')


class ContentError(Exception):
    """An error indicating issues generating content."""

    pass
