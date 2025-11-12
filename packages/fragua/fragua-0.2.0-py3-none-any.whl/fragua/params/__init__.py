"""Fragua ETL Params module."""

# ------------------- Params ------------------- #
from .params import (
    Params,
)

# ------------------- Load Params ------------------- #
from .load_params import (
    LoadParams,
    ExcelLoadParams,
    SQLLoadParams,
    APILoadParams,
    LoadParamsT,
    ExcelLoadParamsT,
    SQLLoadParamsT,
    APILoadParamsT,
)

# ------------------- Extract Params ------------------- #
from .extract_params import (
    ExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
    APIExtractParams,
    ExtractParamsT,
    CSVExtractParamsT,
    ExcelExtractParamsT,
    SQLExtractParamsT,
    APIExtractParamsT,
)

# ------------------- Transform Params ------------------- #
from .transform_params import (
    TransformParams,
    MLTransformParams,
    ReportTransformParams,
    AnalysisTransformParams,
    TransformParamsT,
    MLTransformParamsT,
    ReportTransformParamsT,
    AnalysisTransformParamsT,
)

# ------------------- __all__ ------------------- #
__all__ = [
    "Params",
    # Extract Params
    "ExtractParams",
    "CSVExtractParams",
    "ExcelExtractParams",
    "SQLExtractParams",
    "APIExtractParams",
    "ExtractParamsT",
    "CSVExtractParamsT",
    "ExcelExtractParamsT",
    "SQLExtractParamsT",
    "APIExtractParamsT",
    # Load Params
    "LoadParams",
    "ExcelLoadParams",
    "SQLLoadParams",
    "APILoadParams",
    "LoadParamsT",
    "ExcelLoadParamsT",
    "SQLLoadParamsT",
    "APILoadParamsT",
    # Transform Params
    "TransformParams",
    "MLTransformParams",
    "ReportTransformParams",
    "AnalysisTransformParams",
    "TransformParamsT",
    "MLTransformParamsT",
    "ReportTransformParamsT",
    "AnalysisTransformParamsT",
]
