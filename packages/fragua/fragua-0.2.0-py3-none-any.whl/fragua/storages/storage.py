"""
Base storage class for all storage objects in Fragua (Wagon, Box, Container).
"""

from typing import Generic, Optional, TypeVar
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

T = TypeVar("T")

logger = get_logger(__name__)


class Storage(Generic[T]):
    """Core storage unit containing data and unified metadata handling."""

    def __init__(self, data: Optional[T] = None) -> None:
        self._data: Optional[T] = data
        self._metadata: dict[str, object] = {}

        if data is not None:
            self._generate_base_metadata()

    # --- Properties --- #

    @property
    def data(self) -> T:
        """
        Return the stored data.
        Raises:
            ValueError: if accessed before being initialized.
        """
        if self._data is None:
            raise ValueError(f"{self.__class__.__name__} has no data assigned yet.")
        return self._data

    @data.setter
    def data(self, value: T) -> None:
        """Set or replace the stored data."""
        self._data = value
        self._generate_base_metadata()

    @property
    def metadata(self) -> dict[str, object]:
        """Return the current metadata of the storage."""
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict[str, object]) -> None:
        self._metadata = value

    # --- Internal methods --- #

    def _generate_base_metadata(self) -> None:
        """Generate and attach base metadata."""
        metadata = generate_metadata(self, metadata_type="base")
        add_metadata_to_storage(self, metadata)

    # --- Representation --- #

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
