"""Metadata module."""
from .metadata import Metadata


class MetadataProvider:
    """Provides the Metadata instance."""
    _metadata_class = Metadata

    @staticmethod
    def get_metadata_provider(url):
        """ Get an Metadata instance."""
        return MetadataProvider._metadata_class(url)

    @staticmethod
    def set_metadata_class(metadata_class):
        """
         Set an Metadata class

        :param metadata_class: Metadata or similar compatible class
        """
        MetadataProvider._metadata_class = metadata_class
