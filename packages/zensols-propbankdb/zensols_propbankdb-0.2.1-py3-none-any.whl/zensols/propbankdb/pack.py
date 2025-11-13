"""Package resources for distribution.

"""
__author__ = 'Paul Landes'

from typing import Union
from dataclasses import dataclass, field
import logging
import shutil
from pathlib import Path
from zensols.util import Failure
from zensols.cli import CliHarness, ApplicationError

logger = logging.getLogger(__name__)


@dataclass
class Packager(object):
    """Packages the staged files in to the deployment file.

    """
    stage_dir: Path = field()
    """The directory to where the staged files to be zipped live."""

    archive_dir: Path = field()
    """The directory where the deployment file is created."""

    def pack(self):
        logger.info(f'packaging: {self.stage_dir} -> {self.archive_dir}')
        shutil.make_archive(self.archive_dir, 'zip', self.stage_dir)
