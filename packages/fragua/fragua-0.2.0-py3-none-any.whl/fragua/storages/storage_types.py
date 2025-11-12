"""
Storage types for storing different kinds of data.
"""

from typing import Any, Dict, Union
from fragua.storages.storage import Storage


class Wagon(Storage[Any]):
    """Storage type for raw data."""


class Box(Storage[Any]):
    """Storage type for transformed data."""


class Container(Storage[Any]):
    """
    Storage designed to contain other storages (Wagon and Box).
    """

    def __init__(self) -> None:
        super().__init__(data=None)
        self._content: Dict[str, Union[Wagon, Box]] = {}

    def add_storage(self, storage_name: str, storage: Union[Wagon, Box]) -> None:
        """Add a sub-storage (Wagon or Box) to the container."""
        self._content[storage_name] = storage

    def get_storage(self, name: str) -> Union[Wagon, Box]:
        """Retrieve a specific sub-storage by name."""
        return self._content[name]

    def list_storages(self) -> dict[str, str]:
        """Return a mapping of contained storages: name -> type."""
        return {name: s.__class__.__name__ for name, s in self._content.items()}

    def remove_storage(self, name: str) -> None:
        """Remove a sub-storage by name."""
        self._content.pop(name, None)

    def clear(self) -> None:
        """Remove all contained storages."""
        self._content.clear()

    def __repr__(self) -> str:
        items = ", ".join(self._content.keys()) or "empty"
        return f"<Container: {items}>"


STORAGE_CLASSES: dict[str, type[Storage[Any]]] = {
    "Wagon": Wagon,
    "Box": Box,
    "Container": Container,
}
