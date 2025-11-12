"""Fragua Styles package."""

# ------------------- Base Style ------------------- #
from .style import Style

# ------------------- Load Style Types ------------------- #
from .load_styles import (
    LoadStyle,
    ExcelLoadStyle,
)

# ------------------- Extract Styles ------------------- #
from .extract_styles import (
    ExtractStyle,
    CSVExtractStyle,
    ExcelExtractStyle,
    SQLExtractStyle,
    APIExtractStyle,
)

# ------------------- Transform Styles ------------------- #
from .transform_styles import (
    TransformStyle,
    MLTransformStyle,
    ReportTransformStyle,
    AnalysisTransformStyle,
)


# ------------------- __all__ ------------------- #
__all__ = [
    # Base Styles
    "Style",
    "LoadStyle",
    "ExtractStyle",
    "TransformStyle",
    # Extract Styles
    "CSVExtractStyle",
    "ExcelExtractStyle",
    "SQLExtractStyle",
    "APIExtractStyle",
    # Transform Styles
    "MLTransformStyle",
    "ReportTransformStyle",
    "AnalysisTransformStyle",
    # Load Styles
    "ExcelLoadStyle",
]
