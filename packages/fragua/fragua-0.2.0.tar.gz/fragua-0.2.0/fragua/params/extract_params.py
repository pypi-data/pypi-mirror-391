"""
Extract parameters classes for different types of data sources.
"""

from typing import Any, Dict, Union, TypeVar
from pathlib import Path
from fragua.params.params import Params

# pylint: disable=too-many-arguments, too-many-positional-arguments
# pylint: disable=too-many-instance-attributes


class ExtractParams(Params):
    """Common parameters for extraction agents."""

    def __init__(self, style: str, read_kwargs: Dict[str, Any] | None = None) -> None:
        super().__init__(role="extractor", style=style)
        self.read_kwargs = read_kwargs or {}

    def describe(self) -> str:
        return f"ExtractParams(role={self.role}, style={self.style})"


class CSVExtractParams(ExtractParams):
    """Extraction parameters for CSV files."""

    def __init__(
        self, path: Union[str, Path], read_kwargs: Dict[str, Any] | None = None
    ) -> None:
        super().__init__(style="csv", read_kwargs=read_kwargs)
        self.path = Path(path)

    def describe(self) -> str:
        return f"CSVExtractParams(path='{self.path}')"


class ExcelExtractParams(ExtractParams):
    """Extraction parameters for Excel files."""

    def __init__(
        self,
        path: Union[str, Path],
        sheet_name: Union[str, int] = 0,
        read_kwargs: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(style="excel", read_kwargs=read_kwargs)
        self.path = Path(path)
        self.sheet_name = sheet_name

    def describe(self) -> str:
        return f"ExcelExtractParams(path='{self.path}', sheet_name='{self.sheet_name}')"


class SQLExtractParams(ExtractParams):
    """Extraction parameters for SQL databases."""

    def __init__(self, connection_string: str, query: str) -> None:
        super().__init__(style="sql")
        self.connection_string = connection_string
        self.query = query

    def describe(self) -> str:
        return f"SQLExtractParams(connection='{self.connection_string}', query='{self.query}')"


class APIExtractParams(ExtractParams):
    """Extraction parameters for APIs."""

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] | None = None,
        params: Dict[str, Any] | None = None,
        data: Dict[str, Any] | None = None,
        auth: Dict[str, str] | None = None,
        proxy: Dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(style="api")
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.params = params or {}
        self.data = data or {}
        self.auth = auth or {}
        self.proxy = proxy or {}
        self.timeout = timeout

    def describe(self) -> str:
        return f"APIExtractParams(url='{self.url}', method='{self.method}')"


ExtractParamsT = TypeVar("ExtractParamsT", bound=ExtractParams)
CSVExtractParamsT = TypeVar("CSVExtractParamsT", bound=CSVExtractParams)
ExcelExtractParamsT = TypeVar("ExcelExtractParamsT", bound=ExcelExtractParams)
SQLExtractParamsT = TypeVar("SQLExtractParamsT", bound=SQLExtractParams)
APIExtractParamsT = TypeVar("APIExtractParamsT", bound=APIExtractParams)
