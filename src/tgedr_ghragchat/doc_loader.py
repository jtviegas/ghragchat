"""Document loading utilities.

This module provides:
- DocLoader: loads documents from a configurable source into a destination path.
"""

import logging

from tgedr_dataops_abs.source import Source
from tgedr_ghragchat.settings import Settings
from tgedr_pycommons.utils.reflection import UtilsReflection

logger = logging.getLogger(__name__)


class DocLoader:
    """Loads documents from a configurable source into a destination path."""

    __DEFAULT_SOURCE_IMPLEMENTATION = "tgedr_dataops.source.local_fs_file_source.LocalFsFileSource"

    def __init__(self) -> None:
        """Initialize the loader with no source and default settings."""
        self.__source = None
        self.__settings = Settings()

    def _source(self) -> Source:
        logger.info("[_source|in]")
        if self.__source is None:
            source_impl = self.__settings.source_impl or self.__DEFAULT_SOURCE_IMPLEMENTATION
            elements = source_impl.rsplit(".", 1)
            module_name = elements[0]
            class_name = elements[1]
            self.__source = UtilsReflection.load_subclass_from_module(module_name, class_name, Source)()
        logger.info(f"[_source|out] => {self.__source}")
        return self.__source

    def load(self, src: str, dest: str, suffix: str = ".md") -> None:
        """Load documents from a source into a destination path.

        Args:
            src: Source location to read documents from.
            dest: Destination path to write documents to.
            suffix: File suffix to filter documents by. Defaults to ".md".
        """
        logger.info(f"[get|in] ({src}, {dest}, {suffix})")
        files = self._source().list(context={"source": src, "suffix": suffix})
        self._source().get({"files": files, "target": dest})
        logger.info("[get|out]")
