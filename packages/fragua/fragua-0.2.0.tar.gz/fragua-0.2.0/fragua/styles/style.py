"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from fragua.utils.logger import get_logger
from fragua.params.params import ParamsT

logger = get_logger(__name__)

# ---------------------------------------------------------------------- #
# Type Variables
# ---------------------------------------------------------------------- #
ResultT = TypeVar("ResultT")


class Style(ABC, Generic[ParamsT, ResultT]):
    """
    Abstract base class for all styles in Fragua.
    Defines a standard interface for style operations.

    """

    def __init__(self, style_name: str):
        """Initialize the style with a given name and creator."""
        self.style_name = style_name

    # ---------------------------------------------------------------------- #
    # Abstract Core
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def _run(self, params: ParamsT) -> ResultT:
        """
        Core implementation of the style.

        Must be implemented by subclasses:
        - MineStyle -> extract
        - ForgeStyle -> forge
        - DeliveryStyle -> deliver
        """
        raise NotImplementedError

    def log_error(self, error: Exception) -> None:
        """Log an error with the style context."""
        logger.error(
            "[%s ERROR] %s: %s", self.__class__.__name__, type(error).__name__, error
        )

    # ---------------------------------------------------------------------- #
    # Public pipeline
    # ---------------------------------------------------------------------- #
    def use(self, params: ParamsT) -> ResultT:
        """
        Execute the full style pipeline.
        """
        try:
            result = self._run(params)

            return result

        except Exception as e:
            self.log_error(e)
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} style_name={self.style_name}>"
