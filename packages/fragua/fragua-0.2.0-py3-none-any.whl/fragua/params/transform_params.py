"""
Transform parameters classes for different types of data transformations.
"""

from typing import Any, Dict, TypeVar
from pandas import DataFrame
from fragua.params.params import Params

# pylint: disable=too-many-arguments, too-many-positional-arguments


class TransformParams(Params):
    """Common parameters for transformation agents."""

    def __init__(self, style: str, data: DataFrame) -> None:
        super().__init__(role="transformer", style=style)
        self.data = data

    def describe(self) -> str:
        return f"TransformParams(role={self.role}, style={self.style})"


class MLTransformParams(TransformParams):
    """Parameters for machine learning transformations."""

    def __init__(
        self,
        data: DataFrame,
        target_column: str | None = None,
        categorical_cols: list[str] | None = None,
        numeric_cols: list[str] | None = None,
        outlier_threshold: float | None = None,
    ) -> None:
        super().__init__(style="ml", data=data)
        self.target_column = target_column
        self.categorical_cols = categorical_cols or []
        self.numeric_cols = numeric_cols or []
        self.outlier_threshold = outlier_threshold

    def describe(self) -> str:
        return (
            f"MLTransformParams(target_column='{self.target_column}', "
            f"categorical_cols={self.categorical_cols}, "
            f"numeric_cols={self.numeric_cols})"
        )


class ReportTransformParams(TransformParams):
    """Parameters for report generation transformations."""

    def __init__(
        self,
        data: DataFrame,
        format_config: Dict[str, Any] | None = None,
        derived_columns: Dict[str, str] | None = None,
        rounding_precision: int | None = None,
    ) -> None:
        super().__init__(style="report", data=data)
        self.format_config = format_config or {}
        self.derived_columns = derived_columns or {}
        self.rounding_precision = rounding_precision

    def describe(self) -> str:
        return (
            f"ReportTransformParams(format_config={self.format_config}, "
            f"derived_columns={self.derived_columns}, "
            f"rounding_precision={self.rounding_precision})"
        )


class AnalysisTransformParams(TransformParams):
    """Parameters for data analysis transformations."""

    def __init__(
        self,
        data: DataFrame,
        groupby_cols: list[str] | None = None,
        agg_functions: Dict[str, str] | None = None,
        sort_by: list[str] | None = None,
    ) -> None:
        super().__init__(style="analysis", data=data)
        self.groupby_cols = groupby_cols or []
        self.agg_functions = agg_functions or {}
        self.sort_by = sort_by or []

    def describe(self) -> str:
        return (
            f"AnalysisTransformParams(groupby_cols={self.groupby_cols}, "
            f"agg_functions={self.agg_functions}, sort_by={self.sort_by})"
        )


TransformParamsT = TypeVar("TransformParamsT", bound=TransformParams)
MLTransformParamsT = TypeVar("MLTransformParamsT", bound=MLTransformParams)
ReportTransformParamsT = TypeVar("ReportTransformParamsT", bound=ReportTransformParams)
AnalysisTransformParamsT = TypeVar(
    "AnalysisTransformParamsT", bound=AnalysisTransformParams
)
