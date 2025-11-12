"""
Reusable Functions Module.
"""

# ------------------- Function class ------------------- #
from fragua.functions.function import (
    FraguaFunction,
)

# ------------------- Extract classes ------------------- #
from fragua.functions.extract_functions import (
    ExtractFunction,
    ExcelExtractFunction,
    APIExtractFunction,
    CSVExtractFunction,
    SQLExtractFunction,
)

# ------------------- Transform classes ------------------- #
from fragua.functions.transform_functions import (
    TransformFunction,
    AnalysisTransformFunction,
    ReportTransformFunction,
    MLTransformFunction,
)

# ------------------- Load classes ------------------- #
from fragua.functions.load_functions import (
    LoadFunction,
    ExcelLoadFunction,
)

__all__ = [
    # Function class
    "FraguaFunction",
    # Extract classes
    "ExtractFunction",
    "ExcelExtractFunction",
    "APIExtractFunction",
    "CSVExtractFunction",
    "SQLExtractFunction",
    # Transform classes
    "TransformFunction",
    "AnalysisTransformFunction",
    "ReportTransformFunction",
    "MLTransformFunction",
    # Load classes
    "LoadFunction",
    "ExcelLoadFunction",
]
