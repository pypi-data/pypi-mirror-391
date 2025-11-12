"""
Reusable Load Functions.
"""

import os
from typing import Generic
import pandas as pd


from fragua.functions.function import FraguaFunction
from fragua.params.load_params import (
    ExcelLoadParams,
    ExcelLoadParamsT,
    LoadParamsT,
)


# ----------------------------- #
# --- Excel Helpers --- #
# ----------------------------- #


def validate_excel_params(params: ExcelLoadParams) -> None:
    """
    Validate Excel Load parameters.

    Args:
        params (ExcelLoadParams): Parameters for Excel Load.

    Raises:
        TypeError: If data is not a DataFrame.
        ValueError: If destination folder is missing.
    """
    if not isinstance(params.data, pd.DataFrame):
        raise TypeError("ExcelLoadStyle requires a pandas DataFrame")
    if not params.destination:
        raise ValueError("Destination folder is required")


def build_excel_path(params: ExcelLoadParams) -> str:
    """
    Build the full path for the Excel file, adding '.xlsx' if missing.

    Args:
        params (ExcelLoadParams): Parameters including destination and file_name.

    Returns:
        str: Full path to the Excel file.
    """
    if params.destination is None:
        raise ValueError("'destination' must be provided")

    os.makedirs(params.destination, exist_ok=True)

    if params.file_name is None:
        raise ValueError("'file_name' must be provided")
    _, ext = os.path.splitext(params.file_name)
    file_name = params.file_name if ext else f"{params.file_name}.xlsx"

    return os.path.join(params.destination, file_name)


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert timezone-aware datetime columns to naive datetime.

    Args:
        df (pd.DataFrame): DataFrame to process.

    Returns:
        pd.DataFrame: DataFrame with naive datetime columns.
    """
    datetime_cols = df.select_dtypes(include=["datetimetz"]).columns
    if len(datetime_cols) > 0:
        df = df.copy()
        for col in datetime_cols:
            df[col] = df[col].dt.tz_convert(None)
    return df


def write_excel(df: pd.DataFrame, path: str, sheet_name: str, index: bool) -> None:
    """
    Write or append a DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): DataFrame to write.
        path (str): Full path to Excel file.
        sheet_name (str): Sheet name to write to.
        index (bool): Whether to write the index.
    """
    if os.path.exists(path):
        with pd.ExcelWriter(
            path, mode="a", engine="openpyxl", if_sheet_exists="new"
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)
    else:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)


# ----------------------------- #
# --- CSV Helpers --- #
# ----------------------------- #


# ----------------------------- #
# --- SQL Helpers --- #
# ----------------------------- #


# ----------------------------- #
# --- API Helpers --- #
# ----------------------------- #


# ----------------------------- #
# --- Pipelines --- #
# ----------------------------- #


class LoadFunction(FraguaFunction[LoadParamsT], Generic[LoadParamsT]):
    """
    Represents a Load function in the Fragua framework.
    """

    def __init__(self, name: str, params: LoadParamsT) -> None:
        super().__init__(name=name, action="load", params=params)


class ExcelLoadFunction(LoadFunction[ExcelLoadParamsT]):
    """
    LoadFunction for Excel pipelines.
    """

    def __init__(self, name: str, params: ExcelLoadParamsT) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> pd.DataFrame:
        validate_excel_params(self.params)
        path = build_excel_path(self.params)
        df = convert_datetime_columns(self.params.data)
        write_excel(df, path, self.params.sheet_name or "Sheet1", self.params.index)
        return df
