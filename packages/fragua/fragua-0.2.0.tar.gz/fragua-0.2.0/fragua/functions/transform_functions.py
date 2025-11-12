"""
Reusable Transform Functions.
"""

from __future__ import annotations
from typing import Generic
import numpy as np
import pandas as pd
from pandas.errors import UndefinedVariableError
from sklearn.preprocessing import MinMaxScaler


from fragua.functions.function import FraguaFunction
from fragua.params.transform_params import (
    TransformParamsT,
    MLTransformParamsT,
    ReportTransformParamsT,
    AnalysisTransformParamsT,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# ----------------------------- #
# --- Functions --- #
# ----------------------------- #


def fill_missing(params: TransformParamsT) -> TransformParamsT:
    """
    Fill missing values in numeric and categorical columns.

    Args:
        params (TransformParamsT): Parameters containing the DataFrame and strategy attributes.

    Returns:
        TransformParamsT: Params object with updated data.
    """
    df = params.data.copy()
    numeric_fill = getattr(params, "numeric_fill", "mean")
    categorical_fill = getattr(params, "categorical_fill", "unknown")

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].mean() if numeric_fill == "mean" else 0
            df[col] = df[col].fillna(fill_value)
        else:
            df[col] = df[col].fillna(categorical_fill)

    params.data = df
    logger.info("Transform: Missing values filled.")
    return params


def standardize(params: TransformParamsT) -> TransformParamsT:
    """
    Standardize string columns by trimming and lowering case.

    Args:
        params (TransformParamsT): Parameters containing the DataFrame.

    Returns:
        TransformParamsT: Params object with updated data.
    """
    df = params.data.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
    params.data = df
    logger.info("Transform: String columns standardized.")
    return params


def encode_categoricals(params: TransformParamsT) -> TransformParamsT:
    """
    Encode categorical columns into dummy variables.

    Args:
        params (TransformParamsT): Parameters containing the DataFrame.

    Returns:
        TransformParamsT: Params object with updated data.
    """
    df = params.data.copy()
    cat_cols = df.select_dtypes(include="object").columns
    if len(cat_cols) > 0:
        df = pd.get_dummies(df, columns=cat_cols)
        logger.info("Transform: Encoded categoricals: %s", list(cat_cols))
    params.data = df
    return params


def scale_numeric(params: TransformParamsT) -> TransformParamsT:
    """
    Scale numeric columns using MinMaxScaler.

    Args:
        params (TransformParamsT): Parameters containing the DataFrame.

    Returns:
        TransformParamsT: Params object with updated data.
    """
    df = params.data.copy()
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) > 0:
        scaler = MinMaxScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info("Transform: Scaled numeric columns: %s", list(num_cols))
    params.data = df
    return params


def treat_outliers(params: TransformParamsT) -> TransformParamsT:
    """
    Cap outliers in numeric columns using the IQR method.

    Args:
        params (TransformParamsT): Parameters containing the DataFrame and outlier threshold.

    Returns:
        TransformParamsT: Params object with updated data.
    """
    df = params.data.copy()
    factor = getattr(params, "outlier_threshold", 1.5) or 1.5
    num_cols = df.select_dtypes(include="number").columns

    for col in num_cols:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        df[col] = np.clip(df[col], Q1 - factor * IQR, Q3 + factor * IQR)

    params.data = df
    logger.info("Transform: Outliers treated with factor %.2f", factor)
    return params


def add_derived_columns(params: TransformParamsT) -> TransformParamsT:
    """
    Add derived or computed columns to the DataFrame.

    Args:
        params (TransformParamsT): Parameters containing the DataFrame
                                  and derived column definitions.

    Returns:
        TransformParamsT: Params object with updated data.
    """
    df = params.data.copy()
    derived = getattr(params, "derived_columns", None)

    if derived:
        for new_col, expr in derived.items():
            try:
                df[new_col] = df.eval(expr)
                logger.debug(
                    "Transform: Derived column '%s' created from '%s'.", new_col, expr
                )
            except (UndefinedVariableError, SyntaxError, TypeError, ValueError) as e:
                logger.warning("Transform: Could not compute '%s': %s", new_col, e)
    elif {"quantity", "price"}.issubset(df.columns):
        df["total"] = df["quantity"] * df["price"]
        logger.debug("Transform: Default derived column 'total' added.")

    params.data = df
    return params


def format_numeric(params: TransformParamsT) -> TransformParamsT:
    """
    Format numeric columns by rounding to a given precision.

    Args:
        params TransformParamsT): Parameters containing the DataFrame and rounding precision.

    Returns:
        TransformParamsT: Params object with updated data.
    """
    df = params.data.copy()
    precision = getattr(params, "rounding_precision", 2) or 2
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].round(precision)

    params.data = df
    logger.info("Transform: Numeric columns formatted with precision %d", precision)
    return params


def group_and_aggregate(params: TransformParamsT) -> TransformParamsT:
    """
    Group and aggregate data based on provided columns and aggregation functions.

    Args:
        params (TransformParamsT): Parameters containing DataFrame, groupby_cols, and agg_functions.

    Returns:
        TransformParamsT: Params object with grouped and aggregated data.
    """
    df = params.data.copy()
    groupby_cols = getattr(params, "groupby_cols", []) or []
    agg_functions = getattr(params, "agg_functions", {}) or {}

    if groupby_cols:
        if agg_functions:
            df = df.groupby(groupby_cols).agg(agg_functions).reset_index()
            logger.info(
                "Transform: Grouped by %s with custom aggregations.", groupby_cols
            )
        else:
            df = df.groupby(groupby_cols).agg("sum").reset_index()
            logger.info(
                "Transform: Grouped by %s using default sum aggregation.", groupby_cols
            )

    params.data = df
    return params


def sort_dataframe(params: TransformParamsT) -> TransformParamsT:
    """
    Sort DataFrame by specified columns.

    Args:
        params (TransformParamsT): Parameters containing DataFrame and sort_by attribute.

    Returns:
        TransformParamsT: Params object with sorted data.
    """
    df = params.data.copy()
    sort_by = getattr(params, "sort_by", []) or []

    if sort_by:
        df = df.sort_values(by=sort_by)
        logger.info("Transform: Sorted DataFrame by %s.", sort_by)

    params.data = df
    return params


# ----------------------------- #
# --- Pipelines --- #
# ----------------------------- #


class TransformFunction(FraguaFunction[TransformParamsT], Generic[TransformParamsT]):
    """
    Represents a Transform function in the Fragua framework.
    Used to define transformations applied to extracted data.
    """

    def __init__(self, name: str, params: TransformParamsT) -> None:
        super().__init__(name=name, action="transform", params=params)


class MLTransformFunction(TransformFunction[MLTransformParamsT]):
    """
    TransformFunction for ML pipelines.
    """

    def __init__(self, name: str, params: MLTransformParamsT) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> pd.DataFrame:
        for func in [
            fill_missing,
            standardize,
            encode_categoricals,
            treat_outliers,
            scale_numeric,
        ]:
            self.params = func(self.params)
        return self.params.data


class ReportTransformFunction(TransformFunction[ReportTransformParamsT]):
    """
    TransformFunction for Report pipelines.
    """

    def __init__(self, name: str, params: ReportTransformParamsT) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> pd.DataFrame:
        for func in [
            fill_missing,
            standardize,
            add_derived_columns,
            format_numeric,
        ]:
            self.params = func(self.params)
        return self.params.data


class AnalysisTransformFunction(TransformFunction[AnalysisTransformParamsT]):
    """
    TransformFunction for Analysis pipelines.
    """

    def __init__(self, name: str, params: AnalysisTransformParamsT) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> pd.DataFrame:
        for func in [
            fill_missing,
            standardize,
            group_and_aggregate,
            sort_dataframe,
        ]:
            self.params = func(self.params)
        return self.params.data
