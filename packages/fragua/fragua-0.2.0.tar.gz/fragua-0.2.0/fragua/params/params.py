"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from abc import ABC, abstractmethod
from typing import TypeVar
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Params(ABC):
    """
    Abstract base configuration class for all Fragua parameter types.

    Attributes:
        role (str): Defines the agent role, such as "extractor", "transformer", or "loader".
        style (str): Defines the style or data source type (e.g., "csv", "excel", "sql", "api").
    """

    def __init__(self, role: str, style: str) -> None:
        self.role = role
        self.style = style

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role='{self.role}', style='{self.style}')"

    def to_dict(self) -> dict[str, str]:
        """Return a dictionary representation of the Params object."""
        return {"role": self.role, "style": self.style}

    @abstractmethod
    def describe(self) -> str:
        """Subclasses should implement this to provide a textual summary of their parameters."""


ParamsT = TypeVar("ParamsT", bound=Params)
