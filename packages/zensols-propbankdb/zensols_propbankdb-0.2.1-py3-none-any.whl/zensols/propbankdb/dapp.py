"""A separate CLI entry point for creating the distribution file.  The
distribution file contains the SQLite database file with the frameset structured
data and the embeddings for various facets of the contained role sets.

"""
__author__ = 'Paul Landes'

from dataclasses import dataclass, field
import logging
from zensols.cli import Cleaner
from . import DatabaseLoader
from .embedgen import EmbeddingGenerator
from .pack import Packager

logger = logging.getLogger(__name__)


@dataclass
class LoadApplication(object):
    """Create the deployment distribution file.

    """
    loader: DatabaseLoader = field()
    """Loads the parsed frameset XML files in to an SQLite database."""

    embedding_generator: EmbeddingGenerator = field()
    """Creates sentence embeddings for PropBank objects."""

    packager: Packager = field()
    """Packages the staged files in to the deployment file."""

    cleaner: Cleaner = field()
    """Clean (removes) files the staging files."""

    def _load(self, frameset_limit: int = None):
        """Load the SQLite database from the Frameset XML files.

        :param frameset_limit: the max number of framesets to load

        """
        self.loader.frameset_limit = frameset_limit
        self.loader()
        self.embedding_generator.dump()

    def package(self, frameset_limit: int = None):
        """(Re)create the deployment artifacts and distribution file.

        :param frameset_limit: the max number of framesets to load

        """
        self.cleaner()
        self._load(frameset_limit)
        self.packager.pack()
