"""
Base abstract class for all function schemas used by styles in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic

from fragua.params.params import ParamsT


class FraguaFunction(ABC, Generic[ParamsT]):
    """
    Represents a generic Fragua function that defines a name,
    an action, and an associated Params instance.
    """

    def __init__(self, name: str, action: str, params: ParamsT) -> None:
        self.name: str = name
        self.action: str = action
        self.params: ParamsT = params

    @abstractmethod
    def execute(self) -> Any:
        """
        Executes the function's action. Should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")
