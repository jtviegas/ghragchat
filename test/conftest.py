"""test configurations."""

from pathlib import Path
import sys
import pytest


sys.path.insert(0, Path(__file__).parent.parent.joinpath("src").absolute())  # isort:skip


@pytest.fixture(scope="session")
def resources_folder() -> str:
    """Provides the location of test respource folder.

    Returns:
        test resources folder path

    """
    return Path(__file__).parent.joinpath("resources").absolute()

@pytest.fixture(scope="session")
def data_folder() -> str:
    """Provides the location of test data folder.

    Returns:
        test data folder path

    """
    return Path(__file__).parent.parent.joinpath(".data").absolute()


@pytest.fixture
def temporary_folder(tmp_path: Path) -> Path:
    """Provide a temporary directory unique to each test."""
    return tmp_path
