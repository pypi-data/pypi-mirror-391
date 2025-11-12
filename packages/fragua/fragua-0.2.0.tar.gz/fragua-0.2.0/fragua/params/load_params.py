"""
Load parameters classes for different types of data destinations.
"""

from typing import Dict, TypeVar
from pandas import DataFrame
from fragua.params.params import Params

# pylint: disable=too-many-arguments, too-many-positional-arguments


class LoadParams(Params):
    """Common parameters for loading agents."""

    def __init__(
        self, style: str, data: DataFrame, destination: str | None = None
    ) -> None:
        super().__init__(role="loader", style=style)
        self.data = data
        self.destination = destination

    def describe(self) -> str:
        return f"LoadParams(role={self.role}, style={self.style}, destination={self.destination})"


class ExcelLoadParams(LoadParams):
    """Parameters for Excel load."""

    def __init__(
        self,
        data: DataFrame,
        destination: str | None = None,
        file_name: str | None = None,
        sheet_name: str | None = None,
        index: bool = False,
        engine: str | None = None,
    ) -> None:
        super().__init__(style="excel", data=data, destination=destination)
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.index = index
        self.engine = engine

    def describe(self) -> str:
        return (
            f"ExcelLoadParams(file_name='{self.file_name}', sheet_name='{self.sheet_name}', "
            f"index={self.index}, engine='{self.engine}')"
        )


class SQLLoadParams(LoadParams):
    """Parameters for SQL load."""

    def __init__(
        self,
        data: DataFrame,
        destination: str | None = None,
        table_name: str | None = None,
        if_exists: str = "fail",
        index: bool = False,
        chunksize: int | None = None,
    ) -> None:
        super().__init__(style="sql", data=data, destination=destination)
        self.table_name = table_name
        self.if_exists = if_exists
        self.index = index
        self.chunksize = chunksize

    def describe(self) -> str:
        return (
            f"SQLLoadParams(table_name='{self.table_name}', if_exists='{self.if_exists}', "
            f"index={self.index}, chunksize={self.chunksize})"
        )


class APILoadParams(LoadParams):
    """Parameters for API load."""

    def __init__(
        self,
        data: DataFrame,
        destination: str | None = None,
        endpoint: str | None = None,
        method: str = "POST",
        headers: Dict[str, str] | None = None,
        auth: Dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(style="api", data=data, destination=destination)
        self.endpoint = endpoint
        self.method = method
        self.headers = headers or {}
        self.auth = auth or {}
        self.timeout = timeout

    def describe(self) -> str:
        return f"APILoadParams(endpoint='{self.endpoint}', method='{self.method}')"


LoadParamsT = TypeVar("LoadParamsT", bound=LoadParams)
ExcelLoadParamsT = TypeVar("ExcelLoadParamsT", bound=ExcelLoadParams)
SQLLoadParamsT = TypeVar("SQLLoadParamsT", bound=SQLLoadParams)
APILoadParamsT = TypeVar("APILoadParamsT", bound=APILoadParams)
