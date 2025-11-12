"""
Transform style types for various data transformation scenarios.
"""

from abc import abstractmethod
from typing import Generic

import pandas as pd


from fragua.functions.transform_functions import (
    AnalysisTransformFunction,
    MLTransformFunction,
    ReportTransformFunction,
)
from fragua.styles.style import Style, ResultT
from fragua.utils.logger import get_logger
from fragua.params.transform_params import (
    TransformParamsT,
    MLTransformParamsT,
    ReportTransformParamsT,
    AnalysisTransformParamsT,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Base TransformStyle
# ---------------------------------------------------------------------- #
class TransformStyle(
    Style[TransformParamsT, ResultT], Generic[TransformParamsT, ResultT]
):
    """
    Base class for TransformStyles.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract Transform method (subclasses implement this)
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def transform(self, params: TransformParamsT) -> ResultT:
        """
        Transform the input data according to params.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for Style
    # ---------------------------------------------------------------------- #
    def _run(self, params: TransformParamsT) -> ResultT:
        """
        Executes the TransformStyle transformation step.

        This method is called by Style.use().
        """
        logger.debug("Starting TransformStyle '%s' transformation.", self.style_name)
        result = self.transform(params)
        logger.debug("TransformStyle '%s' transformation completed.", self.style_name)
        return result


# ---------------- MLTransform ----------------
class MLTransformStyle(TransformStyle[MLTransformParamsT, pd.DataFrame]):
    """Transform style for machine learning preprocessing."""

    def transform(self, params: MLTransformParamsT) -> pd.DataFrame:
        return MLTransformFunction("transform_ml", params).execute()


# ---------------- ReportTransform ----------------
class ReportTransformStyle(TransformStyle[ReportTransformParamsT, pd.DataFrame]):
    """Transform style for reporting transformations."""

    def transform(self, params: ReportTransformParamsT) -> pd.DataFrame:
        return ReportTransformFunction("transform_report", params).execute()


# ---------------- AnalysisTransform ----------------
class AnalysisTransformStyle(TransformStyle[AnalysisTransformParamsT, pd.DataFrame]):
    """Transform style for data analysis transformations."""

    def transform(self, params: AnalysisTransformParamsT) -> pd.DataFrame:
        return AnalysisTransformFunction("transform_analysis", params).execute()
