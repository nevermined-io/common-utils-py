"""Metadata module."""
from .metadata import Metadata


class MetadataProvider:
    """Provides the Metadata instance."""
    _metadata_class = Metadata

    @staticmethod
    def get_metadata_provider(url, account=None):
        """ Get an Metadata instance."""
        return MetadataProvider._metadata_class(url, account)

    @staticmethod
    def set_metadata_class(metadata_class):
        """
         Set an Metadata class

        :param metadata_class: Metadata or similar compatible class
        """
        MetadataProvider._metadata_class = metadata_class
