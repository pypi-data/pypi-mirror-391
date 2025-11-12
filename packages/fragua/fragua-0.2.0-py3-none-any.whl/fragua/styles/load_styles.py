"""
LoadStyle types for various data Load methods.
"""

from abc import abstractmethod
from typing import Generic
import pandas as pd


from fragua.functions.load_functions import ExcelLoadFunction
from fragua.styles.style import Style, ResultT
from fragua.params.load_params import (
    LoadParamsT,
    ExcelLoadParamsT,
)
from fragua.utils.logger import get_logger


logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Base LoadStyle
# ---------------------------------------------------------------------- #
class LoadStyle(Style[LoadParamsT, ResultT], Generic[LoadParamsT, ResultT]):
    """
    Base class for all Load styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    @abstractmethod
    def load(self, params: LoadParamsT) -> ResultT:
        """
        load the given data to the target destination.
        Must be overridden by subclasses or use function registry.
        """
        raise NotImplementedError("Subclasses must implement load()")

    def _run(self, params: LoadParamsT) -> ResultT:
        """
        Executes the LoadStyle Load step.
        """
        logger.debug("Starting LoadStyle '%s' Load.", self.style_name)
        result = self.load(params)
        logger.debug("LoadStyle '%s' Load completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# Excel Load
# ---------------------------------------------------------------------- #
class ExcelLoadStyle(LoadStyle[ExcelLoadParamsT, pd.DataFrame]):
    """
    LoadStyle for exporting data to Excel files.
    Uses registered functions for pipeline steps.
    """

    def load(self, params: ExcelLoadParamsT) -> pd.DataFrame:
        return ExcelLoadFunction("load_excel", params).execute()


# ---------------------------------------------------------------------- #
# SQL Load
# ---------------------------------------------------------------------- #


# ---------------------------------------------------------------------- #
# API Load
# ---------------------------------------------------------------------- #
